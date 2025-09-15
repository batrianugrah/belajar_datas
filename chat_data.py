import os
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Load dataset
df = pd.read_csv("dataset.csv")  # Pastikan file ini ada di folder yang sama

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-pro"

tools = [types.Tool(google_search=types.GoogleSearch())]

generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=-1),
    tools=tools,
)

def get_response(user_input):
    # Cek apakah pertanyaan berkaitan dengan dataset
    # 1 Nilai Rata-rata GAD-7
    if "gad-7" in user_input.lower() or "skor" in user_input.lower() or "nilai rata-rata gad" in user_input.lower():
            avg_score = df["GAD7_Score"].mean()
            return f"Rata-rata skor GAD-7 dalam dataset adalah {avg_score:.2f}"
    
    # 2 Jumlah User dengan Skor GAD-7 di atas 10
    elif "diatas 10" in user_input.lower() or "skor diatas 10" in user_input.lower():
        count = df[df["GAD7_Score"] > 10].shape[0]
        return f"Jumlah pengguna dengan skor GAD-7 di atas 10 adalah {count}"
    # 3 Nilai Tertinggi GAD-7        
    elif "nilai tertinggi gad" in user_input.lower() or "nilai maksimum gad" in user_input.lower() or "nilai tertinggi" in user_input.lower():
            max_score = df["GAD7_Score"].max()
            return f"Nilai tertinggi GAD-7 dalam dataset adalah {max_score}"
    
    # 4 Nilai Terendah GAD-7
    elif "nilai terendah gad" in user_input.lower():
            min_score = df["GAD7_Score"].min()
            return f"Nilai terendah GAD-7 dalam dataset adalah {min_score}"
    # 5 User dengan Skor Tertinggi
    elif "user tertinggi" in user_input.lower() or "user dengan skor tertinggi" in user_input.lower():
            top_user = df.loc[df["GAD7_Score"].idxmax(), "User_ID"]
            return f"User dengan skor GAD-7 tertinggi adalah {top_user}"
    
    # 6 Jumlah Data
    elif "jumlah data" in user_input.lower() or "jumlah baris" in user_input.lower():
        try:
            num_rows = df.shape[0]
            return f"Jumlah data dalam dataset adalah {num_rows} baris"
        except Exception as e:
            return f"Gagal membaca data: {e}"
    
    # Jika bukan pertanyaan berbasis data, kirim ke Gemini
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        ),
    ]
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

def chatbot():
    print("Ngajarin Gemini Pakai Data Set GAD-7")
    while True:
        user_input = input("Anda: ")
        if user_input.lower() == "exit":
            print("Chatbot: Sampai jumpa!")
            break
        response = get_response(user_input)
        print("Chatbot:", response)

if __name__ == "__main__":
    chatbot()
