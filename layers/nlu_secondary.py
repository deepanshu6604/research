import google.generativeai as genai
from config import GENAI_MODEL_NAME, GENAI_MAX_TOKENS, GENAI_TEMPERATURE
import json
from layers.memory_system import memory_system
import re
class NLUSecondary:
    def __init__(self):
        self.model = genai.GenerativeModel(GENAI_MODEL_NAME)

    def refine_analysis(self, user_id, text, stm_context, ltm_context):
        """
        Refines insights (intent, emotion, context, etc.) from NLU Primary.
        Uses STM first, LTM only if STM is insufficient, else falls back to primary input.
        """
        system_prompt = f"""
        You are an advanced NLU module responsible for **refining previously extracted analysis**
        using recent session (STM with old user input) and long-term memory (LTM) only for **supportive insights**.

        mix up the refinement task with memory. Only use STM/LTM to **support** your reasoning. 
        the context should refined as sync with the all old analysis and the new user input.
        If STM is insufficient, then check LTM. If both are unavailable or unhelpful, fall back to only the primary analysis.
        and do not loss the old analysis or any information .
        make sure the conversation shuld be synced with the old analysis(along with old inputs) and the new user input.

        Memory:
        STM (current session): {memory_system.get_stm_memory(user_id)}
        LTM (historical context): {ltm_context}

        user input:
        {text}

        ✨ Return this strict JSON:
        ```json
        {{
            "refined_emotion": "frustrated | neutral | happy | etc.",
            "refined_intents": [
                {{
                    "intent": "intent_name",
                    "confidence": 0.9,
                    "priority": 1,
                    "entities": [{{"entity": "value", "type": "type"}}],
                    "negated": false
                }}
            ],
            "overall_refined_emotion": "neutral | happy | frustrated | sad | angry | surprised",
            "refined_conversation_stage": "greeting | smalltalk | request | task | feedback | closing"
            "refined_tone": "formal | casual | excited | etc.",
            "is_sarcastic": true | false,
            "is_ironic": true | false,
            "is_negated": true | false,
            "is_confused": true | false,
            "clarification_required": true | false,
            "feedback_detected": false,
            "user_feedback": only understanding the user feedback text,
            "feedback_type": "positive | negative | neutral",
            "coreference_resolved_input": "Resolved version of user input",
            "language_level": "simple | moderate | complex",
            "disfluencies_detected": true | false,
            "refined_context": "task | scheduling | feedback | etc.",
            "refined_description": "Improved version of what the user wanted",
            "factual_memory_extract": [
                {{
                    "statement": "I live in Delhi",
                    "type": "location",
                    "source": "refined_input"
                }}
            ]
        }}
        ```
        """

        try:
            response = self.model.generate_content(system_prompt, generation_config=genai.GenerationConfig(
                max_output_tokens=GENAI_MAX_TOKENS,
                temperature=GENAI_TEMPERATURE,
            ))
            response_text = response.text.strip() if hasattr(response, "text") else ""
            response_text = response_text.replace("```json", "").replace("```", "").strip()
                                             
            return response_text


        except Exception as e:
            return {"error": f"NLU Secondary Error: {e}"}
        
    def extract_feedback_from_response(self,response_text):
        """
        This function extracts the required feedback fields from the NLU response
        and returns the output in a structured JSON format.

        :param response_text: The raw response text from the NLU model in JSON format.
        :return: A structured JSON object with the required feedback fields.
        """
        try:
            # Parse the response text as JSON
            response_json = json.loads(response_text)
            
            # Extract necessary fields
            extracted_data = {
                "feedback_detected": response_json.get("feedback_detected"),
                "user_feedback": response_json.get("user_feedback"),
                "feedback_type": response_json.get("feedback_type")
            }

            # Return the structured data as a JSON string
            
            return json.dumps(extracted_data, indent=4)

        
        except json.JSONDecodeError:
            return {"error": "Failed to decode the response text into JSON."}
        except Exception as e:
            return {"error": str(e)}
        

    def extract_feedback_data_user_suggestion(self,t):
        # If t is a string, parse it as JSON
        if isinstance(t, str):
            t = "{" + t.strip().rstrip(',') + "}"  # Make sure it’s valid JSON
            data = json.loads(t)
        else:
            data = t  # If it's already a dict

        # Extract values
        user_suggestion = data.get("user_suggestion", "")

        return user_suggestion
    
    def extract_feedback_data_layer_tags(self,t):
        # If t is a string, parse it as JSON
        if isinstance(t, str):
            t = "{" + t.strip().rstrip(',') + "}"  # Make sure it’s valid JSON
            data = json.loads(t)
        
        data = t  # If it's already a dict

        # Extract values
        layer_tags = data.get("layer_tags", [])
        
        return layer_tags
    
    def extract_feedback_data_summary(self,t):
        # If t is a string, parse it as JSON
        if isinstance(t, str):
            t = "{" + t.strip().rstrip(',') + "}"  # Make sure it’s valid JSON
            data = json.loads(t)
        
        
        data = t  # If it's already a dict

        # Extract values
        summary = data.get("summary", "")
        
        return summary
    
    def extract_feedback_data_detected_feedback(self,t):
        if isinstance(t, str):
            t = "{" + t.strip().rstrip(',') + "}"  # Make sure it’s valid JSON
            data = json.loads(t)
        
       
        data = t  # If it's already a dict

        # Extract values
        detected_feedback = data.get("detected_feedback", False)
        
        return detected_feedback
    

    def feedback_analyser(self, user_id, user_feedback):
        """
        Analyzes user feedback from NLU Primary to detect which system layer(s) need improvement.
        Only the feedback text is used for tagging.
        """
        system_prompt = f"""
        **[Feedback Analyzer Layer]**

        🎯 Task:
        Analyze the user feedback text and determine which internal layer(s) require improvement.

        ✅ Use only the statement below:
        "{user_feedback}"

        🧠 Possible system layers to tag:
        - "nlu_primary"
        - "nlu_secondary"
        - "nlg_primary"
        - "nlg_secondary"
        - "stm_to_ltm"
        - "stm_to_factual_memory"
        - "self_thinking_layer"
        - "text_to_voice_layer"
        - "voice_to_text_layer"

        🚦 Return this strict JSON:
        ```json
        {{
            "detected_feedback": true | false,
            "summary": "What user meant",
            "layer_tags": ["layer1", "layer2"],
            "user_suggestion": "Optional fix or improvement if clear"
        }}
        ```
        - If feedback is unclear, return `detected_feedback: false`.
        - Keep reasoning focused and structured.
        """

        try:
            response = self.model.generate_content(system_prompt, generation_config=genai.GenerationConfig(
                max_output_tokens=GENAI_MAX_TOKENS,
                temperature=GENAI_TEMPERATURE,
            ))

            # Extract and clean up response text
            response_text = response.text.strip() if hasattr(response, "text") else ""
            response_text = re.sub(r"```json|```", "", response_text).strip()

            # Extra sanitization (if needed)
            response_text = response_text.replace("True", "true").replace("False", "false")

            # Now attempt to load as JSON
            return json.loads(response_text)

        except Exception as e:
             return {"error": f"Feedback Analyzer Error: {e}"}


# Instance
nlu_secondary = NLUSecondary()
