import io
import os
import streamlit as st
import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment

# Pengaturan Konfigurasi Tampilan
st.set_page_config(
    page_title="Studio Cover Musik & Lirik",
    page_icon="🎵",
    layout="wide"
)

st.title("🎙️ Studio Cover Musik: Ekstraksi Lirik & Aransemen Genre Baru")
st.caption(
    "Ambil informasi lagu referensi, ekstrak lirik otomatis, "
    "lalu gabungkan rekaman cover Anda dengan instrumen genre baru."
)

# ----------------- FUNGSI AUDIO & LIRIK -----------------

def ambil_info_dan_audio(url):
    """Mengunduh audio dari tautan dan mengambil metadata lagu."""
    opsi = {
        "format": "bestaudio/best",
        "outtmpl": "audio_referensi.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opsi) as ydl:
        info = ydl.extract_info(url, download=True)
        judul = info.get("title", "Judul Tidak Diketahui")
        artis = info.get("artist") or info.get("uploader") or "Artis Tidak Diketahui"
        path_file = "audio_referensi.wav"
        return judul, artis, path_file


def transkrip_lirik_ringan(path_audio):
    """Mengekstrak lirik audio secara ringan tanpa membebani RAM server."""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(path_audio) as source:
            data_audio = r.record(source)
            hasil = r.recognize_google(data_audio, language="id-ID")
            return hasil
    except sr.UnknownValueError:
        return "Lirik vokal tidak terdeteksi jelas secara otomatis. Silakan tulis atau edit manual di bawah."
    except Exception as e:
        return f"Catatan: Lirik otomatis tidak dapat dimuat ({e}). Silakan input lirik manual."


# ----------------- SESSION STATE -----------------

if "judul_lagu" not in st.session_state:
    st.session_state["judul_lagu"] = ""
if "penyanyi_lagu" not in st.session_state:
    st.session_state["penyanyi_lagu"] = ""
if "lirik_tersimpan" not in st.session_state:
    st.session_state["lirik_tersimpan"] = ""

# ----------------- STRUKTUR ANTARMUKA -----------------

tab1, tab2 = st.tabs([
    "1. 📥 Ambil Lirik & Info Lagu", 
    "2. 🎛️ Mixing Cover & Rekomendasi YouTube"
])

# --- TAB 1: AMBIL LIRIK & METADATA ---
with tab1:
    st.subheader("Ambil Referensi dari Link Lagu")
    link_input = st.text_input(
        "Masukkan Tautan Lagu (YouTube / URL Video):",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    if st.button("🚀 Ekstrak Info & Lirik", type="primary"):
        if not link_input.strip():
            st.warning("Silakan masukkan tautan lagu terlebih dahulu.")
        else:
            with st.spinner("Sedang memproses audio dan mengenali lirik..."):
                try:
                    judul, artis, file_wav = ambil_info_dan_audio(link_input)
                    teks_lirik = transkrip_lirik_ringan(file_wav)

                    st.session_state["judul_lagu"] = judul
                    st.session_state["penyanyi_lagu"] = artis
                    st.session_state["lirik_tersimpan"] = teks_lirik

                    st.success("Informasi lagu berhasil didapatkan!")
                except Exception as err:
                    st.error(f"Gagal memproses tautan: {err}")

    st.divider()

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.session_state["judul_lagu"] = st.text_input(
            "Judul Lagu Asli:",
            value=st.session_state["judul_lagu"]
        )
    with col_meta2:
        st.session_state["penyanyi_lagu"] = st.text_input(
            "Penyanyi / Artis Asli:",
            value=st.session_state["penyanyi_lagu"]
        )

    st.write("**Lirik Lagu (Bisa disesuaikan ketukannya untuk panduan vokal):**")
    st.session_state["lirik_tersimpan"] = st.text_area(
        label="Lirik Teks:",
        value=st.session_state["lirik_tersimpan"],
        height=260,
        label_visibility="collapsed"
    )

# --- TAB 2: ARANSEMEN GENRE BARU & MIXING ---
with tab2:
    st.subheader("Produksi Musik Cover")

    genre_pilihan = st.selectbox(
        "Target Genre Cover Baru:",
        [
            "Dangdut / Koplo",
            "Reggae / Ska",
            "Akustik / Fingerstyle",
            "Lo-Fi / Chillhop",
            "Pop Punk / Rock",
            "Jazz / Bossa Nova"
        ]
    )

    # Format penulisan video YouTube
    judul_yt = f"{st.session_state['judul_lagu'] or 'Judul Lagu'} - {st.session_state['penyanyi_lagu'] or 'Artis'} (Cover Versi {genre_pilihan})"
    st.markdown("##### 📌 Rekomendasi Format Judul YouTube:")
    st.code(judul_yt, language="text")

    st.divider()

    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown("**1. Rekaman Vokal Baru**")
        file_vokal = st.file_uploader(
            "Unggah suara vokal rekaman Anda:", 
            type=["wav", "mp3", "m4a"], 
            key="upl_vokal"
        )
        vol_vokal = st.slider("Gain Vokal (dB):", -15, 15, 0, key="vol_v")

    with col_u2:
        st.markdown(f"**2. Musik Pengiring ({genre_pilihan})**")
        file_musik = st.file_uploader(
            "Unggah instrumen musik genre baru:", 
            type=["wav", "mp3", "m4a"], 
            key="upl_musik"
        )
        vol_musik = st.slider("Gain Musik (dB):", -15, 15, 0, key="vol_m")

    if st.button("🎚️ Gabungkan Cover & Ekspor", type="primary"):
        if not file_vokal or not file_musik:
            st.error("Silakan unggah kedua file audio terlebih dahulu (vokal dan instrumen).")
        else:
            with st.spinner("Sedang memproses mixing cover..."):
                try:
                    seg_vokal = AudioSegment.from_file(file_vokal) + vol_vokal
                    seg_musik = AudioSegment.from_file(file_musik) + vol_musik

                    # Mixing vokal di atas instrumen mulai dari posisi detik 0
                    hasil_cover = seg_musik.overlay(seg_vokal, position=0)

                    buffer_keluar = io.BytesIO()
                    tag_meta = {
                        "title": f"{st.session_state['judul_lagu']} (Cover {genre_pilihan})",
                        "artist": "Cover Artist",
                        "album": f"Cover of {st.session_state['penyanyi_lagu']}",
                        "genre": genre_pilihan
                    }
                    hasil_cover.export(buffer_keluar, format="mp3", tags=tag_meta)
                    buffer_keluar.seek(0)

                    st.success("Musik cover berhasil dipadukan!")
                    st.audio(buffer_keluar, format="audio/mp3")

                    nama_file_unduh = f"{st.session_state['judul_lagu']}_{genre_pilihan}_Cover.mp3".replace(" ", "_")
                    st.download_button(
                        label="⬇️ Unduh Lagu Cover Siap Upload (MP3)",
                        data=buffer_keluar,
                        file_name=nama_file_unduh,
                        mime="audio/mp3"
                    )
                except Exception as err:
                    st.error(f"Gagal melakukan mixing audio: {err}")
