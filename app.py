import streamlit as st
import yt_dlp
import speech_recognition as sr

st.set_page_config(
    page_title="Suno AI Cover Prompt Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Studio Cover Lagu: Generator Prompt Suno AI")
st.caption("Ambil lirik dari YouTube/Playlist lalu ubah otomatis menjadi Prompt Siap Pakai di Suno AI.")

# ----------------- FUNGSI BACKEND -----------------

def periksa_dan_ambil_daftar(url):
    opsi = {'extract_flat': True, 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(opsi) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            daftar_lagu = []
            for item in info['entries']:
                if item:
                    judul = item.get('title', 'Lagu Tanpa Judul')
                    url_video = item.get('url') or f"https://www.youtube.com/watch?v={item.get('id')}"
                    daftar_lagu.append({'title': judul, 'url': url_video})
            return True, info.get('title', 'Playlist'), daftar_lagu
        else:
            return False, info.get('title', 'Video Tunggal'), [{'title': info.get('title'), 'url': url}]

def unduh_dan_ambil_info(url):
    opsi = {
        "format": "bestaudio/best",
        "outtmpl": "audio_suno.%(ext)s",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opsi) as ydl:
        info = ydl.extract_info(url, download=True)
        judul = info.get("title", "Judul Tidak Diketahui")
        artis = info.get("artist") or info.get("uploader") or "Artis Tidak Diketahui"
        return judul, artis, "audio_suno.wav"

def transkrip_lirik_suno(path_audio):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(path_audio) as source:
            data_audio = r.record(source)
            teks = r.recognize_google(data_audio, language="id-ID")
            # Format dasar untuk struktur Suno AI
            return f"[Verse 1]\n{teks}\n\n[Chorus]\n{teks}\n\n[Outro]"
    except Exception:
        return "[Verse 1]\n(Tulis baris lirik bait pertama di sini)\n\n[Chorus]\n(Tulis baris lirik reff di sini)\n\n[Outro]"

# ----------------- INISIALISASI STATE -----------------

if "daftar_playlist" not in st.session_state:
    st.session_state["daftar_playlist"] = []
if "judul_lagu" not in st.session_state:
    st.session_state["judul_lagu"] = ""
if "penyanyi_lagu" not in st.session_state:
    st.session_state["penyanyi_lagu"] = ""
if "lirik_suno" not in st.session_state:
    st.session_state["lirik_suno"] = ""

# ----------------- ANTARMUKA -----------------

st.subheader("1. Masukkan Tautan Lagu Referensi")
link_input = st.text_input("Tautan YouTube (Video / Playlist):", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🔍 Periksa Tautan", type="primary"):
    if link_input.strip():
        with st.spinner("Membaca informasi tautan..."):
            try:
                is_list, nama_list, items = periksa_dan_ambil_daftar(link_input)
                st.session_state["daftar_playlist"] = items
                st.success(f"Ditemukan {len(items)} lagu.")
            except Exception as e:
                st.error(f"Gagal memuat link: {e}")

if st.session_state["daftar_playlist"]:
    opsi_judul = [item["title"] for item in st.session_state["daftar_playlist"]]
    lagu_terpilih = st.selectbox("Pilih lagu sumber lirik:", opsi_judul)
    url_terpilih = next(item["url"] for item in st.session_state["daftar_playlist"] if item["title"] == lagu_terpilih)

    if st.button("⚡ Ekstrak Info & Siapkan Format Suno"):
        with st.spinner("Mengunduh referensi dan memformat struktur lirik..."):
            try:
                j, a, f = unduh_dan_ambil_info(url_terpilih)
                lirik_terstruktur = transkrip_lirik_suno(f)
                st.session_state["judul_lagu"] = j
                st.session_state["penyanyi_lagu"] = a
                st.session_state["lirik_suno"] = lirik_terstruktur
                st.success("Lirik siap disalin ke Suno!")
            except Exception as err:
                st.error(f"Gagal memproses lagu: {err}")

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
    tempo = st.select_slider("Tempo / Kecepatan:", options=["Slow / Dark", "Medium (120 BPM)", "Fast / Horeg (135-145 BPM)"], value="Fast / Horeg (135-145 BPM)")

# Pembuatan Style Prompt Suno
style_prompt = f"{', '.join(genre_opsi)}, {vokal_tipe}, {tempo}, high quality production"

st.markdown("#### 📋 Hasil Prompt untuk Suno AI (Tinggal Salin)")

col_copy1, col_copy2 = st.columns(2)

with col_copy1:
    st.write("**Salin ke Kolom 'Lyrics' di Suno:**")
    lirik_final = st.text_area("Format Lirik + Tag Birama:", value=st.session_state["lirik_suno"], height=280)

with col_copy2:
    st.write("**Salin ke Kolom 'Style of Music' di Suno:**")
    st.code(style_prompt, language="text")
    
    st.write("**Rekomendasi Judul Lagu di YouTube:**")
    genre_singkat = " x ".join(genre_opsi[:2]) if genre_opsi else "Remix"
    judul_yt = f"{st.session_state['judul_lagu'] or 'Lagu'} - {st.session_state['penyanyi_lagu'] or 'Artis'} (AI Cover {genre_singkat})"
    st.code(judul_yt, language="text")
