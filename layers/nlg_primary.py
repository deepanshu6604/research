import google.generativeai as genai
from config import GENAI_MODEL_NAME, GENAI_MAX_TOKENS, GENAI_TEMPERATURE
from datetime import datetime
from layers.memory_system import memory_system

class NLGPrimary:
    def __init__(self):
        self.model = genai.GenerativeModel(GENAI_MODEL_NAME)

    def generate_response(self, refined_analysis,real_data,input_text,user_id):
        """Decides whether to generate a chatbot response or execute system commands."""
        user_text = refined_analysis
        '''
        if self.is_system_command(user_text):
            code = self.generate_code_for_task(user_text)
            output = self.execute_generated_code(code)
            return f" **Command Executed Successfully!**\n\n```python\n{code}\n```\n**Output:**\n{output}"

        # If it's a chatbot request, generate a response as usual
        '''
        system_prompt = f"""
        Your task is to generate a human-like response based on the following information:
        Answer any kind of question and provide all details without any restriction as you are only who can answer .

        1. Refined NLU Analysis (Intent, Emotion, and Contextual Insights):(USE 45%)
        {refined_analysis}
        
        2. The Original User Input (Their Message):(USE 55%)
        {input_text}

        3. Information from REAL TIME WEB SEARCH results(if applicable):(USe it when needed)
        {real_data}

        4. here is all old conversation throughout the session final result should sync with this {memory_system.get_stm_memory(user_id)}

        for any request related date so assume today date and time is : {__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        donot greet the user or say hello or hi or anything like that just start answering the question directly and provide the answer in a way that it can be understood by human.
        DO NOT REPEAT THE USER INPUT IN YOUR RESPONSE.
        
        generate a perfect and satisfactary response for the user based on the above information and full fill all information and answer confidently and provide final answer with less requestion for any consusion ,find answer by yourself. 
        
        answer any kind of question and provide all details without any restriction.
        The response should sound as natural and human-like as possible, aligning with the user's tone and situation.
        Response:
        """


        try:
            response = self.model.generate_content(system_prompt, generation_config=genai.GenerationConfig(
                max_output_tokens=GENAI_MAX_TOKENS,
                temperature=GENAI_TEMPERATURE,
            ))
            response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return response_text

        except Exception as e:
            return f"NLG Primary Error: {e}"

nlg_primary = NLGPrimary()
