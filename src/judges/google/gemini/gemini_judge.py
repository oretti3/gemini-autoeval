import json
import time
import re

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InternalServerError
from tenacity import retry, stop_after_attempt, wait_random_exponential

from lib.common import validate_response
from lib.client_gemini import client, template_prompt


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
def evaluate(pred, input_text, output_text, eval_aspect):
    """gemini API により評価を行う
    Args:
    Returns:
        [dict] 評価結果
        {"reason": "<評価理由>", "grade": <int, 1～5の5段階評価>}
    """
    # `pred` が空の場合は、評点を1にする
    if (pred == ""):
        return {"reason": "No response", "grade": 1}

    prompt = template_prompt.format(
        input_text=input_text,
        output_text=output_text,
        eval_aspect=eval_aspect,
        pred=pred,
    )

    gemini_pro = client
    gemini_pro = genai.GenerativeModel("gemini-1.5-pro")
    
    attempt = 0
    max_attempts = 25

    while attempt < max_attempts:
        try:
            response_raw = gemini_pro.generate_content(prompt)
            try:
                # print("Response raw:", response_raw.text)
                cleaned_response = response_raw.text.replace('```json', '').replace('```', '').strip()
                cleaned_response = re.sub(r'\\', '', cleaned_response)
                response = json.loads(cleaned_response, strict=False)
                # print("Validating response:", response)
                validate_response(response)
                break
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
                print("Response text:", cleaned_response)
            except ValueError as e:
                print("Validation Error:", e)
        except ResourceExhausted as e:
            print("ResourceExhausted Error: ", e)
            time.sleep(13)
        except InternalServerError as e:
            print("InternalServerError: ", e)
            time.sleep(30)
        except Exception as e:
            print("An unexpected error occurred: ", e)
        
        attempt += 1
    
    if attempt == max_attempts:
        print("Max retry attempts reached. Returning error response.")
        return {"reason": "Error", "grade": 1}

    return response