import streamlit as st
import yt_dlp

st.set_page_config(
    page_title="Suno AI Prompt Studio",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Studio Cover Lagu: Generator Prompt Suno AI")
st.caption("Anti-Error 403: Ambil info lagu tanpa unduh file besar, lalu siapkan prompt Suno AI.")

def ambil_info_saja(url):
    """Hanya mengambil judul dan artis tanpa download stream video/audio."""
    opsi = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(opsi) as ydl:
        info = ydl.extract_info(url, download=False)
        judul = info.get("title", "Judul Tidak Diketahui")
        artis = info.get("artist") or info.get("uploader") or "Artis Tidak Diketahui"
        return judul, artis

# State
if "judul" not in st.session_state:
    st.session_state["judul"] = ""
if "artis" not in st.session_state:
    st.session_state["artis"] = ""
if "lirik" not in st.session_state:
    st.session_state["lirik"] = "[Verse 1]\n\n[Chorus]\n\n[Outro]"

st.subheader("1. Masukkan Tautan Lagu Referensi")
link = st.text_input("Tautan YouTube:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("⚡ Ambil Info Lagu", type="primary"):
    if link.strip():
        with st.spinner("Membaca data lagu..."):
            try:
                j, a = ambil_info_saja(link)
                st.session_state["judul"] = j
                st.session_state["artis"] = a
                st.success(f"Berhasil memuat info: {j}")
            except Exception as e:
                st.error(f"Gagal memuat link: {e}")

st.divider()

st.subheader("2. Konfigurasi Gaya Musik (Suno Style Prompt)")

col_g1, col_g2 = st.columns(2)

with col_g1:
    genre_opsi = st.multiselect(
        "Pilih Komponen Genre:",
        options=[
            "Indonesian DJ Horeg", "Sub-bass Glerr 30Hz", "Dangdut Koplo",
            "Kendang Rampak", "Heavy Metal", "Distorted Guitar",
            "Mistis Etnik Jawa Gamelan Horor", "Dark Ambient", "Rock",
            "EDM Dutch Trap", "Breakbeat", "Jedag Jedug"
        ],
        default=["Indonesian DJ Horeg", "Sub-bass Glerr 30Hz", "Dangdut Koplo"]
    )

with col_g2:
    vokal_tipe = st.selectbox(
        "Karakter Vokal Suno:",
        ["Energetic Male Vocal", "Powerful Female Vocal", "Heavy Metal Growl / Scream", "Sinden Mystical Female Vocal", "Raw Indonesian Vocal"]
    )
    tempo = st.select_slider(
        "Tempo / Kecepatan:", 
        options=["Slow / Dark", "Medium (120 BPM)", "Fast / Horeg (135-145 BPM)"], 
        value="Fast / Horeg (135-145 BPM)"
    )

style_prompt = f"{', '.join(genre_opsi)}, {vokal_tipe}, {tempo}, punchy beat, high quality production"

st.markdown("#### 📋 Hasil Prompt untuk Suno AI (Tinggal Salin)")

col_copy1, col_copy2 = st.columns(2)

with col_copy1:
    st.write("**Kolom Lirik (Tempel lirik lagu di antara tag birama):**")
    st.session_state["lirik"] = st.text_area(
        "Lyrics Structure:",
        value=st.session_state["lirik"],
        height=260
    )

with col_copy2:
    st.write("**Salin ke Kolom 'Style of Music' di Suno:**")
    st.code(style_prompt, language="text")
    
    st.write("**Rekomendasi Judul Lagu di YouTube:**")
    genre_singkat = " x ".join(genre_opsi[:2]) if genre_opsi else "Remix"
    judul_yt = f"{st.session_state['judul'] or 'Lagu'} - {st.session_state['artis'] or 'Artis'} (AI Cover {genre_singkat})"
    st.code(judul_yt, language="text")
