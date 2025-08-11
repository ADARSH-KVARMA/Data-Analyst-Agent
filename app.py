# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "flask",
#   "python-dotenv",
#   "google-generativeai",
#   "openai",
#   "flask-cors",
# ]
# ///

from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import dotenv
import os
import re 
import json

app = Flask(__name__)

# Load environment variables from .env file
dotenv.load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)
full_prompt = """
You are an expert Data Analyst agent capable of analyzing data with high accuracy.
Always respond only in the JSON format exactly as specified in the question. Also response should  be like ```json ... ``.
Do not include any explanations, commentary, or extra text.
If you cannot find the exact answer, provide a possible or example JSON response instead — never state “I don’t know.”
"""

def llm_response_to_json(llm_response: str):
    # Extract content between triple backticks
    match = re.search(r"```json\s*(.*?)\s*```", llm_response, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON block found in LLM response.")
    
    json_str = match.group(1).strip()
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

def get_ans_with_gpt(question_string: str, prompt_template: str) -> None:
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    full_prompt = f"{prompt_template.strip()}\nUser Question:\n{question_string.strip()}"

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=full_prompt
        )

        # Extract the model's reply text
        instructions = response.output_text
        return instructions

    except Exception as e:
        print(f"[❌] Error generating steps: {e}")

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

@app.route("/", methods=["GET"])
def main():
    return "<h1> Angent is only for personal use as of now </h1>"

@app.route("/api/", methods=["POST"])
def upload_files():
    """
    Handles one or more uploaded files in a single POST request.
    """
    if 'files' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist("files")
    file_info_list = []

    for file in files:
        if file.filename == 'question.txt' :
            try:
                content = file.read()
                question_string = str(content)

                file_size = len(content)
                file_info_list.append({
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size_in_bytes": file_size,
                })
            except Exception as e:
                file_info_list.append({
                    "filename": file.filename,
                    "error": str(e)
                })


    ans = get_ans_with_gpt(question_string=question_string, prompt_template=full_prompt)
    json_ans = llm_response_to_json(ans)

    return json_ans


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

