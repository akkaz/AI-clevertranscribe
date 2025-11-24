import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AnalysisService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        self.client = OpenAI(api_key=api_key)

    def generate_title(self, text: str) -> str:
        """
        Generate a short, semantic title for the transcription.
        """
        prompt = f"""
        Based on the following meeting transcription, generate a short, descriptive title (maximum 5 words).
        The title should capture the main topic or purpose of the meeting.
        
        Transcription:
        {text[:500]}...
        
        Respond with ONLY the title, nothing else.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use cheaper model for title generation
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates concise meeting titles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=20
            )
            
            title = response.choices[0].message.content.strip()
            # Remove quotes if present
            title = title.strip('"\'')
            return title
        except Exception as e:
            print(f"Error generating title: {e}")
            return "Untitled Meeting"

    def analyze_transcription(self, text: str, model: str = "gpt-4o", custom_prompt: str = None) -> dict:
        """
        Analyze the transcription to extract a To-Do list and a Meeting Report.
        """
        base_prompt = """
        You are an expert AI assistant. Analyze the following meeting transcription and provide:
        1. A list of "To Do" items.
        2. A concise meeting report summarizing the key points, decisions, and next steps.
        """
        
        if custom_prompt:
            base_prompt += f"\n\nAdditional Instructions:\n{custom_prompt}"

        prompt = f"""
        {base_prompt}

        Transcription:
        {text}

        Format the output as a JSON object with keys "todo_list" (list of strings) and "report" (string).
        """

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes meeting transcriptions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            import json
            return json.loads(content)
        except Exception as e:
            print(f"Error during analysis: {e}")
            return {"todo_list": [], "report": "Error generating report."}
