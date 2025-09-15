prompt_A = """Product description: A pair of shoes that can
fit any foot size.
Seed words: adaptable, fit, omni-fit.
Product names:"""

prompt_B = """Product description: A home milkshake maker.
Seed words: fast, healthy, compact.
Product names: HomeShaker, Fit Shaker, QuickShake, Shake
Maker

Product description: A watch that can tell accurate time in
space.
Seed words: astronaut, space-hardened, eliptical orbit
Product names: AstroTime, SpaceGuard, Orbit-Accurate,
EliptoTime.

Product description: A pair of shoes that can fit any foot
size.
Seed words: adaptable, fit, omni-fit.
Product names:"""

test_prompts = [prompt_A, prompt_B]

import os
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-pro"

tools = [types.Tool(google_search=types.GoogleSearch())]

generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=-1),
    tools=tools,
)

def get_response(prompt):
    contents = [
        # Bagian konten yang berisi input dari pengguna
        types.Content(
            # Bagian peran yang menunjukkan bahwa ini adalah input dari pengguna
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    # Menggunakan client untuk menghasilkan konten secara streaming
    try:
        response = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            response += chunk.text
        return response
    except Exception as e:
        return f"Terjadi kesalahan: {e}"

responses = [] # untuk menyimpan respons dari model
num_tests = 5 # jumlah pengulangan untuk setiap prompt

for idx, prompt in enumerate(test_prompts):
    # prompt number as a letter
    var_name = chr(ord('A') + idx)

    for i in range(num_tests):
        # Get a response from the model
        response = get_response(prompt)

        data = {
            "variant": var_name,
            "prompt": prompt, 
            "response": response
            }
        responses.append(data)

# Convert responses into a dataframe
df = pd.DataFrame(responses)

# Save the dataframe as a CSV file
df.to_csv("responses.csv", index=False)

print(df)