import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Setting API Key dan Model yang digunakan 
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-pro"

# Definisikan tools yang akan digunakan, dalam hal ini Google Search untuk mencari informasi secara online
tools = [types.Tool(google_search=types.GoogleSearch())]

# Konfigurasi untuk generate content, kreativitas berpikir (-1)
generate_content_config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=-1),
    tools=tools,
)

# Fungsi untuk mendapatkan respons dari chatbot dengan nama user_input
def get_response(user_input):
    contents = [
        # Bagian konten yang berisi input dari pengguna
        types.Content(
            # Bagian peran yang menunjukkan bahwa ini adalah input dari pengguna
            role="user",
            parts=[types.Part.from_text(text=user_input)],
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

# Fungsi utama untuk menjalankan chatbot, variabel user_input akan diisi dengan input dari pengguna dan dikirim ke fungsi get_response
def chatbot():
    print("🤖 Chatbot Gemini - Ketik 'exit' untuk keluar")
    while True:
        user_input = input("Apa yang ingin kamu tanyakan ?: ")
        if user_input.lower() == "exit":
            print("Chatbot: Sampai jumpa!")
            break
        # Mendapatkan respons dari chatbot berdasarkan input pengguna
        response = get_response(user_input)
        # Menampilkan respons dari chatbot
        print("Chatbot:", response)
# Menjalankan fungsi chatbot jika file ini dieksekusi sebagai program utama
if __name__ == "__main__":
    chatbot()
