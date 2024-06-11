import google.generativeai as genai

with open("./assets/prompt_eval.txt") as f:
    template_prompt = f.read()

with open("/run/secrets/GEMINI_API_KEY") as f:
    GEMINI_API_KEY = f.read()

client = genai.configure(api_key=GEMINI_API_KEY)