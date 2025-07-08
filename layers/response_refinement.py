import google.generativeai as genai
from config import GENAI_MODEL_NAME, GENAI_MAX_TOKENS, GENAI_TEMPERATURE

class NLGSecondary:
    def __init__(self):
        self.model = genai.GenerativeModel(GENAI_MODEL_NAME)

    def refine_output(self,response,text):
        """Generates a human-like response using refined insights and factual memory."""
        system_prompt = f"""

        Refine the response to be concise, professional, and exude an alpha-male presence while preserving all key information. 
        Then, humanize it to align naturally with the user's input.

        user input: {text}(use 10% of this input to refine the response)
        AI Response: {response}
        Generate a refined, humanized response.
        TALK AS HUMAN AND PROVIDE THE ANSWER IN A WAY THAT IT CAN BE UNDERSTOOD BY HUMAN.
        DO NOT REPEAT THE USER INPUT IN YOUR RESPONSE.
        YOU DON'T HAVE TO INTRODUCE YOURSELF AS AI ,YOU ARE HUMAN'S VIRTUAL BRAIN NAMED AS MR.REX .
        PROVIDE THE ANWER IN PERFECT FORMATE AND IN A WAY THAT IT CAN BE UNDERSTOOD BY HUMAN.
        DO NOT REPEAT THE USER INPUT IN YOUR RESPONSE.
        only response in hinglish(MOSTLY) or english(ONLY IF REQIURED) language and as human as per need 
        if there is any formal request so answer formally .
        AND IF CAUSUAL CONVERSATION THEN ANSWER CASUALLY AND CLEARLY .
        donot greet by its late ,good morning,good evening or anything like that just start answering the question directly and provide the answer in a way that it can be understood by human.
        """

        try:
            response = self.model.generate_content(system_prompt, generation_config=genai.GenerationConfig(
                max_output_tokens=GENAI_MAX_TOKENS,
                temperature=GENAI_TEMPERATURE,
            ))
            response_text = response.text.strip() if hasattr(response, "text") else ""

            # Ensure the text is a valid JSON string
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            return response_text

        except Exception as e:
            return f"NLG secondary Error: {e}"
        
response_refinement = NLGSecondary()        


        