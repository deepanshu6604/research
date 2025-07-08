import requests
import google.generativeai as genai
import json
import re
from config import GENAI_MODEL_NAME, GENAI_MAX_TOKENS, GENAI_TEMPERATURE

class KnowledgeBaseSearch:
    def __init__(self):
        self.google_api_key = "AIzaSyA45MAtJ9n2EEZihPHLk9DGLWqtxVrWXu4"
        self.search_engine_id = "26e7976d160204ee7"
        self.gemini_api_key = "AIzaSyCPJOknpdRBaBJpy-sEcUTdOXdpEE2ztLI"
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        genai.configure(api_key=self.gemini_api_key)

    def is_web_search_required(self, user_input, refined_analysis):
        """
        Decides if web search is necessary using Gemini logic.
        """
        prompt = f"""
        Decide whether a real-time web search is needed or not.
        User Input: {user_input}
        Refined Analysis: {refined_analysis}

        Respond only with "yes" or "no".
        """
        response = self.gemini_model.generate_content(prompt)
        answer = response.text.strip().lower()
        return "yes" if "yes" in answer else "no"

    def perfect_prompt_converter(self, need_search, refined_analysis, user_input):
        """
        Converts the user's input and context into an optimal search engine prompt.
        """
        if need_search != "yes":
            return "NOT APPLICABLE"

        prompt = f"""
        You are a search query optimizer. Convert the following into a clean, direct search query:
        - Context: {refined_analysis}
        - User Input: {user_input}

        Focus on keywords and remove unnecessary parts. Return only the optimized search string.
        """
        response = self.gemini_model.generate_content(prompt)
        cleaned_input = self.extract_json_from_response(response)
        return cleaned_input if isinstance(cleaned_input, str) else response.text.strip()

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
            response_text = response_text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")

            return json.loads(response_text)
        except json.JSONDecodeError:
            return response_text
        except Exception:
            return response_text

    def google_custom_search_api(self, query, api_key, cx_id, num_results=5):
        """
        Fetches search results from Google Custom Search API.
        """
        url = f"https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cx_id,
            'q': query,
            'num': num_results
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            })
        return results

    def convert_snippets_to_answer(self, results):
        """
        Converts search result snippets into a final answer using Gemini.
        """
        if not results:
            return "NOT APPLICABLE"

        combined_content = "\n\n".join(
            f"Title: {item['title']}\nSnippet: {item['snippet']}" for item in results
        )
        prompt = (
            "Using the following search results, generate a short, accurate, and informative answer:\n\n"
            f"{combined_content}"
        )

        response = self.gemini_model.generate_content(prompt)
        return response.text.strip() if response and response.text else "NOT APPLICABLE"

    def run_pipeline(self, user_input, reff):
        """
        Main pipeline: Decide need, convert prompt, search web, return final answer.
        """
        refined_analysis = f"{reff} — {user_input}"
        need_search = self.is_web_search_required(user_input, refined_analysis)

        if need_search == "yes":
            converted_prompt = self.perfect_prompt_converter(need_search, refined_analysis, user_input)
            search_results = self.google_custom_search_api(converted_prompt, self.google_api_key, self.search_engine_id)
            final_answer = self.convert_snippets_to_answer(search_results)
        else:
            converted_prompt = "NOT APPLICABLE"
            final_answer = self.gemini_model.generate_content(
                f"Answer based on internal knowledge only: {user_input}"
            ).text.strip()

        if not final_answer:
            final_answer = "NOT APPLICABLE"

        return {
            "need_search": need_search,
            "converted_prompt": converted_prompt,
            "final_answer": final_answer
        }


# Example Usage:
web_searcher = KnowledgeBaseSearch()
# result = web_searcher.run_pipeline("What is the latest update on Chandrayaan?", "Chandrayaan 3 launch details")
# print(result)
