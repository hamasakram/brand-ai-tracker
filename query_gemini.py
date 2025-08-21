import os
from google import genai
import yaml

# Load API key from environment (do not hardcode secrets)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable")

client = genai.Client(api_key=api_key)

# Load prompts from local file
base_dir = os.path.dirname(os.path.abspath(__file__))
prompts_path = os.path.join(base_dir, "prompts.yaml")
with open(prompts_path, "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f).get("prompts", [])

for prompt in prompts:
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",  # free-tier model
        contents=prompt["text"],
    )
    print(f"\n--- Prompt: {prompt['text']}")
    print(getattr(response, "text", response))
