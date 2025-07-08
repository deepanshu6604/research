from config import GENAI_MODEL_NAME, GENAI_MAX_TOKENS, GENAI_TEMPERATURE
import google.generativeai as genai
import json
import re

class NLUPrimary:
    def __init__(self):
        self.model = genai.GenerativeModel(GENAI_MODEL_NAME)

    def extract_json_from_response(self, response_text):
        """
        Cleans Gemini's response and extracts JSON safely.
        """
        try:
            # Remove code block markers
            response_text = response_text.strip()
            response_text = re.sub(r"^```json", "", response_text, flags=re.IGNORECASE).strip()
            response_text = re.sub(r"```$", "", response_text).strip()

            # Fix common issues
            response_text = response_text.replace("True", "true").replace("False", "false").replace("None", "null")

            # Replace curly quotes with straight quotes
            response_text = response_text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

            # Attempt to load JSON
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            return {
                "error": f"JSONDecodeError: {str(e)}",
                "raw_output": response_text
            }
        except Exception as e:
            return {
                "error": f"Exception while parsing: {str(e)}",
                "raw_output": response_text
            }

    def analyze(self, text):
        """
        Analyzes the input text and returns structured JSON with:
        - Intents, emotion, context, task segmentation, and more.
        """
        system_prompt = f"""
        You are an advanced Natural Language Understanding (NLU) module in a voice-based AI system.

        Your task is to analyze the user's input and return a structured JSON response that includes:
        - One or more user intents (with confidence, entities, and negation status)
        - Emotion, tone, sarcasm, confusion, irony, disfluencies, feedback, etc.
        - A summarized one-word context and a short description
        - Factual memory statements (to be stored and reused in future conversations)
        - only suggest the feedback for understanding mistakes of user's text

        You must handle long, complex, multi-intent user inputs clearly and return precise fields.

        --- Input:
        {text}

        --- Output:
        Return only valid JSON in the following format. Do NOT include markdown (no ```json or explanations).

        {{
            "intents": [
                {{
                    "intent": "intent_name",
                    "confidence": 0.91,
                    "priority": 1,
                    "entities": [
                        {{
                            "entity": "actual_value",
                            "type": "entity_type"
                        }}
                    ],
                    "negated": false
                }}
            ],
            "overall_emotion": "neutral | happy | frustrated | sad | angry | surprised",
            "tone": "formal | casual | excited | polite | annoyed",
            "conversation_stage": "greeting | smalltalk | request | task | feedback | closing",
            "is_sarcastic": true,
            "is_ironic": false,
            "is_negated": false,
            "is_confused": false,
            "clarification_required": false,
            "feedback_detected": false,
            "user_feedback": null,
            "coreference_resolved_input": "Rephrased version of input with pronouns resolved",
            "language_level": "simple | moderate | complex",
            "code_switched": false,
            "disfluencies_detected": false,
            "context": "scheduling | cancelation | reminder | weather | travel | info | jobsearch | personal | project | resume | feedback | etc.",
            "description": "The user asked to set an alarm, check schedule for tomorrow, and cancel a gym appointment.",
            "factual_memory_extract": [
                {{
                    "statement": "I am from Bhopal.",
                    "type": "location",
                    "source": "user_input"
                }},
                {{
                    "statement": "I know Python and Django.",
                    "type": "skills",
                    "source": "user_input"
                }}
            ]
        }}
        """

        try:
            response = self.model.generate_content(
                system_prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=GENAI_MAX_TOKENS,
                    temperature=GENAI_TEMPERATURE,
                )
            )

            response_text = response.text.strip() if hasattr(response, "text") else ""

            # Debug: print raw response (optional)
            # print("Raw Gemini output:\n", response_text)

            return self.extract_json_from_response(response_text)

        except Exception as e:
            return {"error": f"NLU Analysis Error: {e}"}
nlu_primary = NLUPrimary()