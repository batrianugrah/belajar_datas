import streamlit as st
import base64
import os
import re
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
# config model
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-flash"
grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

# Prompt Builder
def build_prompt(title, keywords, article_length, tone, audience, language):
    return [
            f"Generate a Blogspot article with the following details:",
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
                5. Keep paragraphs short (2 to 4 sentences) for mobile readability.
                6. Add bullet points or numbered lists when listing information.
                7. Include internal links (suggest 1 to 2 links to related blog posts) and external links to reputable sources.
                8. Suggest at least 2 relevant images with keyword-rich alt text for better SEO.
                9. Provide an optimized URL slug suggestion (short, keyword-focused, no stop words).
                10. End with a strong conclusion and a clear call-to-action (e.g., share, comment, follow).
                11. Ensure the article is SEO-friendly, readable, and engaging for the target audience.
            """,
            f"""If the instructions about sex, violence content and hate speech, return massage : "Sorry, I can't assist with that request." and stop the process.""" 
    ]

# New function to extract SEO details from the generated text
def extract_seo_details(text):
    meta_desc = re.search(r"Meta Description:\s*(.*)", text)
    url_slug = re.search(r"URL Slug:\s*(.*)", text)
    alt_texts = re.findall(r"Image Alt Text:\s*(.*)", text)
    
    return {
        "meta_description": meta_desc.group(1).strip() if meta_desc else "Tidak ditemukan.",
        "url_slug": url_slug.group(1).strip() if url_slug else "Tidak ditemukan.",
        "alt_texts": [alt.strip() for alt in alt_texts]
    }

##########################Front End Streamlit##########################

# set ke wide mode
st.set_page_config(layout="wide")
# judul aplikasi
st.title("⚡️ HyperWrite | untuk penulis yang memiliki jadwal padat dan membutuhkan konten yang cepat, tetapi tetap berkualitas")
# subheader
st.subheader("Buat Blog Otomatis gratis- support by Hacktiv8")
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
    num_images = st.number_input("Jumlah Gambar)", min_value=0, max_value=3, value=0)
    # temperature
    temperature = st.slider("Kreatifitas (semakin tinggi semakin ngaco)", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    # tombol submit
    submit_button = st.button("Buat Artikel Blog")

# Generate Button
if submit_button:
    if not title or not keywords:
        st.warning("Judul dan kata kunci tidak boleh kosong.")
    else:
        prompt_parts = build_prompt(title, keywords, article_length, tone, audience, language)

        with st.status("Sedang membuat artikel...", expanded=True) as status:
            try:
                # Part 1: Text Generation
                status.update(label="🚀 Sedang menulis draf artikel...")
                response = client.models.generate_content(
                    model=model,
                    contents=[prompt_parts],
                    config=types.GenerateContentConfig(
                        tools=[grounding_tool],
                        temperature=temperature,
                        top_p=0.8,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                        safety_settings=[
                             types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
                             types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
                             types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_ONLY_HIGH"),
                             types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
                        ]
                    )
                )

                if response.text == "Sorry, I can't assist with that request.":
                    st.warning(response.text)
                    status.update(label="Proses dibatalkan.", state="error")
                else:
                    st.success("✅ Artikel berhasil dibuat!")
                    
                    # Part 2: SEO Extraction
                    status.update(label="🔍 Mengekstrak detail SEO...")
                    seo_details = extract_seo_details(response.text)
                    st.header("Detail SEO")
                    st.markdown(f"**Meta Description:** {seo_details['meta_description']}")
                    st.markdown(f"**URL Slug:** {seo_details['url_slug']}")

                    # Part 3: Display Article
                    st.header(title)
                    st.write(response.text)
                    
                    # Part 4: Download Button
                    st.download_button(
                        label="Unduh Artikel",
                        data=response.text,
                        file_name=f"{seo_details['url_slug']}.txt",
                        mime="text/plain"
                    )

                    # Part 5: Image Generation (improved)
                    if num_images > 0 and seo_details['alt_texts']:
                        status.update(label="🖼️ Sedang membuat gambar...", state="running")
                        st.subheader("Gambar yang Disarankan")
                        for i in range(min(num_images, len(seo_details['alt_texts']))):
                            alt_text = seo_details['alt_texts'][i]
                            try:
                                img_response = client.models.generate_content(
                                    model="gemini-2.0-flash-preview-image-generation",
                                    contents=f"High-quality image for blog article, based on alt text: {alt_text}",
                                    config=types.GenerateContentConfig(
                                        response_modalities=['IMAGE']
                                    )
                                )
                                for part in img_response.candidates[0].content.parts:
                                    if part.inline_data:
                                        image = Image.open(BytesIO(part.inline_data.data))
                                        st.image(image, caption=alt_text)
                            except Exception as e:
                                st.warning(f"Gagal membuat gambar untuk '{alt_text}'. Pesan error: {e}")
                    status.update(label="🎉 Selesai!", state="complete")
            except Exception as e:
                status.update(label="Terjadi kesalahan dalam proses.", state="error")
                st.error(f"Terjadi kesalahan: {e}")