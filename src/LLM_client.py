import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


def get_gemini_client():
    """
    Creates and returns a Gemini client.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")

    return genai.Client(api_key=api_key)


def ask_analyst(prompt: str, system_instruction: str = None) -> str:
    """
    Sends a prompt to Gemini and returns the generated text.
    """
    try:
        client = get_gemini_client()

        config = {}

        if system_instruction:
            config["system_instruction"] = system_instruction

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=config if config else None,
        )

        return response.text

    except Exception as e:
        return f"Error communicating with Gemini:\n{e}"