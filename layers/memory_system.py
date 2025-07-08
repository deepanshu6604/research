import pymongo
import sqlite3
import google.generativeai as genai
import json
from config import MONGO_URI, MONGO_DB_NAME, MONGO_STM_COLLECTION, MONGO_LTM_COLLECTION, SQLITE_DB_PATH, GENAI_MODEL_NAME, GENAI_MAX_TOKENS, GENAI_TEMPERATURE
from datetime import datetime
from bson import ObjectId

class MemorySystem:
    def __init__(self):
        # Connect to MongoDB
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]
        self.stm_collection = self.db[MONGO_STM_COLLECTION]
        self.ltm_collection = self.db[MONGO_LTM_COLLECTION]
        self.factual_memory_collection = self.db["factual_memory"]

        # Connect to SQLite for feedback storage
        self.sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        self.sqlite_cursor = self.sqlite_conn.cursor()

        # Ensure feedback table exists
        self.sqlite_cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                user_id TEXT,
                feedback TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.sqlite_conn.commit()

    def store_in_stm(self, user_id, user_input, analysis):
        """
        Stores user input and analysis in STM. If more than 5 entries exist, removes the oldest one.
        Returns the ID of the inserted STM entry.
        """
        # Fetch current STM records
        stm_entries = list(self.stm_collection.find({"user_id": user_id}))

        # Insert new STM entry (includes user input and analysis)
        inserted_entry = self.stm_collection.insert_one({
            "user_id": user_id,
            "user_input": user_input,
            "analysis": analysis,
            "timestamp": datetime.utcnow()
        })    
        
        # If STM exceeds 10 entries, remove the oldest
        if len(stm_entries) >= 10:
            oldest_entry = stm_entries[0]  # First inserted entry
            self.stm_collection.delete_one({"_id": oldest_entry["_id"]})

        return str(inserted_entry.inserted_id)  # Return ID of the inserted STM record
        
    def update_stm_with_output(self, stm_id, chatbot_output):
        """
        Updates the specified STM entry with the chatbot's generated output.
        """
        result = self.stm_collection.update_one(
            {"_id": ObjectId(stm_id)},  # Find document by ID
            {"$set": {"chatbot_output": chatbot_output}}  # Update with chatbot's response
        )
        
        if result.modified_count > 0:
            return f"Updated STM entry {stm_id} with chatbot output."
        else:
            return f"Failed to update STM entry {stm_id}."
    

    def generate_summary_from_full_stm(self, user_id):
        """
        Summarizes all STM entries of a user and converts them into structured LTM format.
        """
        # Fetch ALL STM entries for the user
        stm_entries = list(self.stm_collection.find({"user_id": user_id}))

        if not stm_entries:
            return None  # No data to process

        # Extract the 'analysis' field (or 'text' if you prefer raw input)
        analysis_texts = [entry.get("analysis", "") for entry in stm_entries if entry.get("analysis")]

        # Build the Gemini AI prompt
        system_prompt = f"""
        You are an AI chatbot memory summarizer. Your task is to summarize the entire conversation history stored 
        in short-term memory (STM) and output a structured long-term memory (LTM) record.

        Instructions:
        - Read all entries carefully.
        - Identify key patterns, recurring topics, emotional tones, intents, and preferences.
        - Summarize everything in a structured JSON format suitable for storage in LTM.

        Format Example:
        {{
            "summary": "Full summary of user's session...",
            "key_topics": ["example topic 1", "example topic 2"],
            "dominant_emotion": "neutral / happy / confused / angry / ...",
            "patterns_detected": ["user tends to...", "frequent questions about..."],
            "user_preferences": "Summarized preferences in short format.",
            "important_statements": ["important insight 1", "important message 2"]
        }}

        STM Entries:
        {json.dumps(analysis_texts, indent=2)}
        """

        try:
            model = genai.GenerativeModel(GENAI_MODEL_NAME)
            response = model.generate_content(
                system_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=GENAI_MAX_TOKENS,
                    temperature=GENAI_TEMPERATURE,
                )
            )

            raw_output = getattr(response, "text", "").replace("```json", "").replace("```", "").strip()

            # Parse output JSON from Gemini
            summary_data = json.loads(raw_output)

            # Final LTM structure
            structured_summary = {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": summary_data.get("summary", ""),
                "key_topics": summary_data.get("key_topics", []),
                "dominant_emotion": summary_data.get("dominant_emotion", ""),
                "patterns_detected": summary_data.get("patterns_detected", []),
                "user_preferences": summary_data.get("user_preferences", ""),
                "important_statements": summary_data.get("important_statements", [])
            }

            return structured_summary

        except json.JSONDecodeError:
            return {"error": f"Invalid JSON returned: {raw_output}"}
        except Exception as e:
            return {"error": f"Summary Generation Error: {e}"}

    def transfer_stm_to_ltm(self, user_id):
        """
        Generates a summary of STM and stores it in LTM.
        """
        summary = self.generate_summary_from_full_stm(user_id)

        if summary and "error" not in summary:
            self.ltm_collection.insert_one({"user_id": user_id, "ltm_summary": summary})
            self.delete_stm_entries(user_id)  # Delete STM entries after transfer
            return "Summary added to LTM."
            
        return "No STM data to summarize."
    
    def delete_stm_entries(self, user_id):
        """
        Deletes all STM entries for a given user_id.
        """
        result = self.stm_collection.delete_many({"user_id": user_id})
        
        if result.deleted_count > 0:
            return f"Deleted {result.deleted_count} STM entries for user {user_id}."
        return f"No STM entries found for user {user_id}."

    
    def get_ltm_context(self, user_id):
        """
        Retrieves full LTM context (all summaries) for a given user.
        """
        ltm_entries = list(self.ltm_collection.find({"user_id": user_id}))
        if not ltm_entries:
            k="ltm is empty"
            return k  # No LTM data found

        # Extract all ltm_summary fields from all entries
        all_ltm_summaries = [entry.get("ltm_summary", {}) for entry in ltm_entries]
        return all_ltm_summaries
    
    def get_stm_memory(self, user_id):
        """
        Retrieves all STM memory entries for a given user.
        """
        stm_entries = list(self.stm_collection.find({"user_id": user_id}))
        return stm_entries if stm_entries else None

memory_system = MemorySystem()
