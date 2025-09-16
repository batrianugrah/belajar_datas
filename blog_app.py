import streamlit as st
import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


# config model

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

model = "gemini-2.5-flash-lite"

tools = [
    types.Tool(googleSearch=types.GoogleSearch(
    )),
]

generate_content_config = types.GenerateContentConfig(
    temperature=0.7,
    top_p=0.8,
    top_k=20,
    thinking_config=types.ThinkingConfig(thinking_budget=0),

    safety_settings=[
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="BLOCK_ONLY_HIGH",  # Block few
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="BLOCK_ONLY_HIGH",  # Block few
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="BLOCK_ONLY_HIGH",  # Block few
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_ONLY_HIGH",  # Block few
        ),
],
    tools=tools  
)

##########################Front End Streamlit##########################
# set ke wide mode
st.set_page_config(layout="wide")

# judul aplikasi
st.title("💻 Aplikasi Chat Bot Pembuatan Blog Otomatis dengan Gemini-2.5")

# subheader
st.subheader("Buat Blog Otomatis dengan Gemini-2.5 tanpa coding dan gratis")

# bagian sidebar
with st.sidebar:
    st.title("Input detail artikel blog")
    st.subheader("Masukkan detail artikel blog yang ingin dibuat")
    
    # input judul artikel
    blog_title = st.text_input("Judul Artikel")
    keywords = st.text_area("Kata Kunci (pisahkan dengan koma)")

    # input panjang artikel
    article_length = st.slider("Panjang Artikel (dalam kata)", min_value=300, max_value=1000, step=100, value=250)
    tone = st.selectbox("Pilih Gaya Bahasa", options=["Resmi", "Santai", "Persuasif", "Informatif"], index=1)
    audience = st.selectbox("Pilih Audiens", options=["Umum", "Profesional", "Pelajar", "Hobiis"], index=0)
    language = st.selectbox("Pilih Bahasa", options=["Indonesia", "English", "Spanish", "French"], index=0)

    # Jumlah Gambar
    num_images = st.number_input("Jumlah Gambar (1-3)", min_value=1, max_value=3, value=2, step=1)
    
    prompt_parts = [
        f"Generate a Blogspot article with the following details:",
        f"Write a {article_length}-word blog post in {language} about '{blog_title}'",
        f"Use a {tone.lower()} tone suitable for a {audience.lower()} audience.",
        f"Include the following keywords: {keywords}.",
        "Structure the content with an introduction, body, and conclusion.",
        "Ensure the content is engaging and informative.",
        "Provide image suggestions relevant to the content."
        """Important Instructions:
            - Start with a strong and engaging introduction (hook).  
            - Use clear headings and subheadings (H2, H3) for readability.  
            - Naturally incorporate the keywords throughout the article without keyword stuffing.  
            - Ensure the writing style is engaging, informative, and SEO-friendly.  
            - Keep paragraphs short (2 up to 4 sentences) for better readability.  
            - Conclude with a call-to-action or thought-provoking closing statement."""       
    ]
    # model_id = 'gemini-2.5-flash'
    response = client.models.generate_content(
            model=model,
            contents= [prompt_parts]
    )

 # tombol generate
    submit_button = st.button("Generate Blog")
    if submit_button:
        st.write(response.text)