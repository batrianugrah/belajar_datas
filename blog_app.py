import streamlit as st
import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
# config model
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-flash"

# Konfigurasi Nodel
def get_generation_config():
     return types.GenerateContentConfig(
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
        tools=[types.Tool(googleSearch=types.GoogleSearch())]
     )
# Prompt Builder
def build_prompt(title, keywords, article_length, tone, audience, language):
    return [
            f"You are an expert SEO copywriter. Generate a Blogspot article with the following details:",
            f"Title: {title}",
            f"Keywords: {keywords}",
            f"Article Length: {article_length} words",
            f"Tone: {tone}",
            f"Audience: {audience}",
            f"Language: {language}",
            f"""SEO and Writing Instructions:
                1. Start with a strong, engaging introduction (hook) that includes the main keyword.
                2. Write a short and persuasive meta description (150 to 160 characters) containing the main keyword.
                3. Use H2 and H3 headings for clear structure. Insert keywords naturally in some headings.
                4. Place the main keyword in the first paragraph, a few times in the body, and once in the conclusion.
                5. Keep paragraphs short (2to 4 sentences) for mobile readability.
                6. Add bullet points or numbered lists when listing information.
                7. Include internal links (suggest 1 to 2 links to related blog posts) and external links to reputable sources.
                8. Suggest at least 2 relevant images with keyword-rich alt text for better SEO.
                9. Provide an optimized URL slug suggestion (short, keyword-focused, no stop words).
                10. End with a strong conclusion and a clear call-to-action (e.g., share, comment, follow).
                11. Ensure the article is SEO-friendly, readable, and engaging for the target audience.
            """
            
            
            # f"Generate a Blogspot article with the following details:",
            # f"Write a {article_length}-word blog post in {language} about '{title}'.",
            # f"Use a {tone.lower()} tone suitable for a {audience.lower()} audience.",
            # f"Include the following keywords: {keywords}.",
            
            # """Important Instructions:
            # - Start with a strong and engaging introduction (hook).  
            # - Use clear headings and subheadings (H2, H3) for readability.  
            # - Naturally incorporate the keywords throughout the article without keyword stuffing.  
            # - Ensure the writing style is engaging, informative, and SEO-friendly.  
            # - Keep paragraphs short (2 up to 4 sentences) for better readability.  
            # - Conclude with a call-to-action or thought-provoking closing statement."""
    ]

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
    title = st.text_input("Judul Artikel")
    keywords = st.text_area("Kata Kunci (pisahkan dengan koma)")

    # input panjang artikel
    article_length = st.slider("Panjang Artikel (dalam kata)", min_value=300, max_value=1000, step=100, value=300)
    tone = st.selectbox("Pilih Gaya Bahasa", options=["Formal", "Casual", "Persuade", "Informatif"], index=0)
    audience = st.selectbox("Pilih Audiens", options=["General", "Profesionals", "Student", "Hobies"], index=0)
    language = st.selectbox("Pilih Bahasa", options=["Indonesian", "English", "Spanish", "French"], index=0)

    # Jumlah Gambar
    num_images = st.number_input("Jumlah Gambar (1-3)", min_value=1, max_value=3, value=2)
    submit_button = st.button("Buat Artikel Blog")

# Generate Button
if submit_button:
    if not title or not keywords:
        st.warning("Judul dan kata kunci tidak boleh kosong.")
    else:
        prompt_parts = build_prompt(title, keywords, article_length, tone, audience, language)

    with st.spinner("Sedang membuat artikel..."):
        response = client.models.generate_content(
            model=model,
            contents=[prompt_parts],
            #generation_config=get_generation_config()
        )
        st.success("✅ Artikel berhasil dibuat!")
        st.write(response.text)