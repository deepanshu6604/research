import openai
from config import OPENAI_MODEL_NAME, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from datetime import datetime
from layers.memory_system import memory_system
openai.api_key = "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"
class NLGPrimary:
    def __init__(self):
        self.model_name = OPENAI_MODEL_NAME  # e.g., "gpt-4" or "gpt-3.5-turbo"

    def generate_response(self, refined_analysis, real_data, input_text, user_id):
        """Generates a high-quality natural language response using OpenAI API."""
        try:
            stm_memory = memory_system.get_stm_memory(user_id)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a highly capable and confident AI assistant. "
                        "Your job is to provide natural, complete, and helpful responses "
                        "based on multiple sources of information. Never greet the user or repeat their question. "
                        "Start directly with the answer. Avoid asking unnecessary clarifications—make intelligent assumptions if needed."
                    )
                },
                {
                    "role": "user",
                    "content": f"""
                    Generate a helpful, human-like response using the information below:

                    1. Refined NLU Analysis (Intent, Emotion, Context) – USE ~45%:
                    {refined_analysis}

                    2. Original User Input – USE ~55%:
                    {input_text}

                    3. Real-Time Web Search Data (if applicable):
                    {real_data}

                    4. Session Memory (Prior Conversation Context):
                    {stm_memory}

                    5. Current Date & Time (if needed):
                    {current_time}

                    ⚠️ Instructions:
                    - DO NOT greet or say "Hi".
                    - DO NOT repeat the user's question.
                    - Provide a complete, satisfactory answer in a natural tone.
                    - If any information is missing, intelligently infer or assume instead of asking.
                    - Sound confident and aligned with the user's intent and emotion.
                    """
                },
            ]

            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE,
            )

            return response.choices[0].message['content'].strip()

        except Exception as e:
            return f"NLG Primary Error: {e}"

nlg_primary = NLGPrimary()
