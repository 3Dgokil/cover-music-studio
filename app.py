import io
import os
import streamlit as st
import yt_dlp
from faster_whisper import WhisperModel
from pydub import AudioSegment

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Studio Cover Musik & Lirik",
    page_icon="🎵",
    layout="wide"
)

st.title("🎙️ Studio Cover Musik: Ekstraksi Lirik & Aransemen Genre Baru")
st.caption(
    "Ambil informasi lagu referensi, ekstrak lirik otomatis via AI Whisper, "
    "lalu gabungkan vokal cover Anda dengan musik aransemen genre baru."
)

# ----------------- FUNGSI BACKEND -----------------

def ambil_info_dan_audio(url):
    """Mengambil metadata lagu dan mengekstrak audio MP3 dari tautan video."""
    opsi = {
        "format": "bestaudio/best",
        "outtmpl": "audio_sumber_temp.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(opsi) as ydl:
        info = ydl.extract_info(url, download=True)
        judul = info.get("title", "Judul Tidak Diketahui")
        artis = info.get("artist") or info.get("uploader") or "Artis Tidak Diketahui"
        path_file = "audio_sumber_temp.mp3"
        return judul, artis, path_file


def transkrip_lirik_whisper(path_audio):
    """Mengekstrak lirik lagu menggunakan model faster-whisper."""
    # Menggunakan model 'small' pada CPU agar ringan dan cepat di cloud server
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(path_audio, beam_size=5)
    lirik_teks = "\n".join([seg.text.strip() for seg in segments if seg.text.strip()])
    return lirik_teks


# ----------------- INISIALISASI STATE -----------------

if "judul_lagu" not in st.session_state:
    st.session_state["judul_lagu"] = ""
if "penyanyi_lagu" not in st.session_state:
    st.session_state["penyanyi_lagu"] = ""
if "lirik_tersimpan" not in st.session_state:
    st.session_state["lirik_tersimpan"] = ""

# ----------------- TAMPILAN TABS -----------------

tab1, tab2 = st.tabs([
    "1. 📥 Sumber Lagu & Ekstraksi Lirik", 
    "2. 🎛️ Mixing Cover & Rekomendasi YouTube"
])

# --- TAB 1: EKSTRAKSI LIRIK ---
with tab1:
    st.subheader("Ambil Referensi dari Link Lagu")
    link_input = st.text_input(
        "Masukkan Tautan (YouTube / Video URL):",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    if st.button("🚀 Ekstrak Info & Lirik Otomatis", type="primary"):
        if not link_input.strip():
            st.warning("Silakan masukkan tautan lagu terlebih dahulu.")
        else:
            with st.spinner("Mengunduh referensi dan memproses lirik dengan Whisper AI..."):
                try:
                    judul, artis, file_audio = ambil_info_dan_audio(link_input)
                    lirik_hasil = transkrip_lirik_whisper(file_audio)

                    st.session_state["judul_lagu"] = judul
                    st.session_state["penyanyi_lagu"] = artis
                    st.session_state["lirik_tersimpan"] = lirik_hasil

                    st.success("Informasi dan lirik berhasil diekstrak!")
                except Exception as err:
                    st.error(f"Gagal memproses tautan: {err}")

    st.divider()

    # Kolom info lagu yang terdeteksi (bisa diedit pengguna)
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

    # Area teks lirik hasil transkrip
    st.write("**Lirik Lagu (Bisa diedit ketukannya untuk panduan bernyanyi):**")
    st.session_state["lirik_tersimpan"] = st.text_area(
        label="Lirik Teks:",
        value=st.session_state["lirik_tersimpan"],
        height=260,
        label_visibility="collapsed"
    )

# --- TAB 2: ARANSEMEN GENRE BARU & MIXING ---
with tab2:
    st.subheader("Produksi Musik Cover Genre Baru")

    genre_pilihan = st.selectbox(
        "Pilih Target Genre Baru:",
        [
            "Dangdut / Koplo",
            "Reggae / Ska",
            "Akustik / Fingerstyle",
            "Lo-Fi / Chillhop",
            "Pop Punk / Rock",
            "Jazz / Bossa Nova"
        ]
    )

    # Format rekomendasi penulisan judul YouTube
    nama_lagu = st.session_state["judul_lagu"] if st.session_state["judul_lagu"] else "Judul Lagu"
    nama_artis = st.session_state["penyanyi_lagu"] if st.session_state["penyanyi_lagu"] else "Artis"
    format_judul_yt = f"{nama_lagu} - {nama_artis} (Cover Versi {genre_pilihan})"

    st.markdown("##### 📌 Rekomendasi Format Judul YouTube:")
    st.code(format_judul_yt, language="text")

    st.divider()

    # Form Unggah Audio Cover
    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown("**1. Rekaman Vokal Baru**")
        file_vokal = st.file_uploader(
            "Unggah suara vokal Anda:", 
            type=["wav", "mp3", "m4a"], 
            key="upl_vokal"
        )
        vol_vokal = st.slider("Gain Vokal (dB):", -15, 15, 0, key="vol_v")

    with col_u2:
        st.markdown(f"**2. Musik Pengiring ({genre_pilihan})**")
        file_musik = st.file_uploader(
            "Unggah instrumen musik baru:", 
            type=["wav", "mp3", "m4a"], 
            key="upl_musik"
        )
        vol_musik = st.slider("Gain Musik (dB):", -15, 15, 0, key="vol_m")

    # Tombol Eksekusi Mixing
    if st.button("🎚️ Gabungkan Cover & Terapkan Metadata", type="primary"):
        if not file_vokal or not file_musik:
            st.error("Silakan unggah kedua file audio (vokal cover dan instrumen musik baru).")
        else:
            with st.spinner("Sedang menggabungkan instrumen dan vokal..."):
                try:
                    segmen_vokal = AudioSegment.from_file(file_vokal) + vol_vokal
                    segmen_musik = AudioSegment.from_file(file_musik) + vol_musik

                    # Menyatukan trek vokal di atas instrumen mulai dari detik 0
                    hasil_gabungan = segmen_musik.overlay(segmen_vokal, position=0)

                    buffer_output = io.BytesIO()
                    # Menambahkan ID3 tags metadata ke dalam file audio
                    tag_meta = {
                        "title": f"{nama_lagu} (Cover {genre_pilihan})",
                        "artist": "Cover Artist",
                        "album": f"Cover Version of {nama_artis}",
                        "genre": genre_pilihan
                    }
                    hasil_gabungan.export(buffer_output, format="mp3", tags=tag_meta)
                    buffer_output.seek(0)

                    st.success("Lagu cover berhasil digabungkan!")
                    st.audio(buffer_output, format="audio/mp3")

                    nama_file_unduh = f"{nama_lagu}_{genre_pilihan}_Cover.mp3".replace(" ", "_")
                    st.download_button(
                        label="⬇️ Unduh Lagu Cover Siap Upload (MP3)",
                        data=buffer_output,
                        file_name=nama_file_unduh,
                        mime="audio/mp3"
                    )
                except Exception as err:
                    st.error(f"Terjadi kendala saat mixing audio: {err}")
