import io
import os
import streamlit as st
import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment

st.set_page_config(
    page_title="Studio Cover Musik & Lirik",
    page_icon="🎵",
    layout="wide"
)

st.title("🎙️ Studio Cover Musik: Ekstraksi Lirik & Aransemen Multi-Genre")
st.caption("Eksplorasi perpaduan gaya unik: Metal, Mistis, Rock, Dangdut, hingga EDM Horeg.")

# ----------------- FUNGSI BACKEND -----------------

def periksa_dan_ambil_daftar(url):
    opsi = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
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
        "outtmpl": "audio_terpilih.%(ext)s",
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
        path_file = "audio_terpilih.wav"
        return judul, artis, path_file


def transkrip_lirik_ringan(path_audio):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(path_audio) as source:
            data_audio = r.record(source)
            hasil = r.recognize_google(data_audio, language="id-ID")
            return hasil
    except sr.UnknownValueError:
        return "Lirik vokal tidak terdeteksi otomatis. Silakan tulis atau perbaiki manual di bawah."
    except Exception as e:
        return f"Catatan: Lirik otomatis tidak dapat dimuat ({e}). Silakan input lirik manual."


# ----------------- INISIALISASI STATE -----------------

if "daftar_playlist" not in st.session_state:
    st.session_state["daftar_playlist"] = []
if "judul_lagu" not in st.session_state:
    st.session_state["judul_lagu"] = ""
if "penyanyi_lagu" not in st.session_state:
    st.session_state["penyanyi_lagu"] = ""
if "lirik_tersimpan" not in st.session_state:
    st.session_state["lirik_tersimpan"] = ""

# ----------------- TAMPILAN -----------------

tab1, tab2 = st.tabs([
    "1. 📥 Ambil Lirik & Info Lagu", 
    "2. 🎛️ Mixing Cover & Rekomendasi YouTube"
])

# --- TAB 1 ---
with tab1:
    st.subheader("Ambil Referensi Lagu (Link Video / Playlist)")
    link_input = st.text_input(
        "Masukkan Tautan (YouTube Video / Playlist URL):",
        placeholder="https://www.youtube.com/watch?v=... atau link playlist"
    )

    if st.button("🔍 Cek Tautan / Muat Daftar", type="primary"):
        if not link_input.strip():
            st.warning("Silakan tempel tautan terlebih dahulu.")
        else:
            with st.spinner("Membaca informasi tautan..."):
                try:
                    is_playlist, nama_list, items = periksa_dan_ambil_daftar(link_input)
                    st.session_state["daftar_playlist"] = items
                    if is_playlist:
                        st.success(f"Playlist terdeteksi: **{nama_list}** ({len(items)} lagu ditemukan).")
                    else:
                        st.success(f"Video ditemukan: **{items[0]['title']}**")
                except Exception as err:
                    st.error(f"Gagal memuat link: {err}")

    if st.session_state["daftar_playlist"]:
        opsi_judul = [item["title"] for item in st.session_state["daftar_playlist"]]
        lagu_terpilih = st.selectbox("Pilih lagu yang akan dicover:", opsi_judul)
        
        url_terpilih = next(
            item["url"] for item in st.session_state["daftar_playlist"] if item["title"] == lagu_terpilih
        )

        if st.button("🚀 Ambil Data & Ekstrak Lirik Lagu Terpilih"):
            with st.spinner(f"Mengunduh audio dan memproses '{lagu_terpilih}'..."):
                try:
                    judul, artis, file_wav = unduh_dan_ambil_info(url_terpilih)
                    teks_lirik = transkrip_lirik_ringan(file_wav)

                    st.session_state["judul_lagu"] = judul
                    st.session_state["penyanyi_lagu"] = artis
                    st.session_state["lirik_tersimpan"] = teks_lirik
                    st.success("Lirik dan info lagu berhasil diproses!")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat mengunduh: {e}")

    st.divider()

    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.session_state["judul_lagu"] = st.text_input(
            "Judul Lagu:",
            value=st.session_state["judul_lagu"]
        )
    with col_meta2:
        st.session_state["penyanyi_lagu"] = st.text_input(
            "Penyanyi / Artis:",
            value=st.session_state["penyanyi_lagu"]
        )

    st.write("**Lirik Lagu (Bisa diedit/disesuaikan ketukannya):**")
    st.session_state["lirik_tersimpan"] = st.text_area(
        label="Lirik Teks:",
        value=st.session_state["lirik_tersimpan"],
        height=240,
        label_visibility="collapsed"
    )

# --- TAB 2 ---
with tab2:
    st.subheader("Produksi Musik Cover")

    pilihan_genre_list = [
        "EDM Horeg (Glerr Trap / Dutch Style)",
        "DJ Horeg / Bass Sub Glerr",
        "Heavy Metal",
        "Metal / Hardcore",
        "Rock / Classic Rock",
        "Mistis / Etnik Horor (Gamelan & Supranatural Ambience)",
        "Dangdut / Koplo",
        "Jedag Jedug / Bassboost",
        "Reggae / Ska",
        "Akustik / Fingerstyle",
        "Lo-Fi / Chillhop",
        "Jazz / Bossa Nova"
    ]

    genre_terpilih = st.multiselect(
        "Pilih Kombinasi Genre Cover (Bisa pilih lebih dari 1 untuk digabung):",
        options=pilihan_genre_list,
        default=["EDM Horeg (Glerr Trap / Dutch Style)", "Dangdut / Koplo"]
    )

    label_genre = " x ".join(genre_terpilih) if genre_terpilih else "Custom Style"

    judul_yt = f"{st.session_state['judul_lagu'] or 'Judul Lagu'} - {st.session_state['penyanyi_lagu'] or 'Artis'} (Cover Versi {label_genre})"
    st.markdown("##### 📌 Rekomendasi Format Judul YouTube:")
    st.code(judul_yt, language="text")

    st.divider()

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("**1. Rekaman Vokal Baru**")
        file_vokal = st.file_uploader("Unggah vokal baru Anda:", type=["wav", "mp3", "m4a"], key="upl_vokal")
        vol_vokal = st.slider("Gain Vokal (dB):", -15, 15, 0, key="vol_v")

    with col_u2:
        st.markdown(f"**2. Musik Pengiring ({label_genre})**")
        file_musik = st.file_uploader("Unggah instrumen musik hasil aransemen:", type=["wav", "mp3", "m4a"], key="upl_musik")
        vol_musik = st.slider("Gain Musik (dB):", -15, 15, 0, key="vol_m")

    if st.button("🎚️ Gabungkan Cover & Ekspor", type="primary"):
        if not file_vokal or not file_musik:
            st.error("Silakan unggah kedua file audio terlebih dahulu.")
        else:
            with st.spinner("Sedang memproses mixing cover..."):
                try:
                    seg_vokal = AudioSegment.from_file(file_vokal) + vol_vokal
                    seg_musik = AudioSegment.from_file(file_musik) + vol_musik

                    hasil_cover = seg_musik.overlay(seg_vokal, position=0)

                    buffer_keluar = io.BytesIO()
                    tag_meta = {
                        "title": f"{st.session_state['judul_lagu']} (Cover {label_genre})",
                        "artist": "Cover Artist",
                        "album": f"Cover of {st.session_state['penyanyi_lagu']}",
                        "genre": label_genre
                    }
                    hasil_cover.export(buffer_keluar, format="mp3", tags=tag_meta)
                    buffer_keluar.seek(0)

                    st.success("Musik cover berhasil dipadukan!")
                    st.audio(buffer_keluar, format="audio/mp3")

                    nama_file_rapi = f"{st.session_state['judul_lagu']}_{label_genre}_Cover.mp3".replace(" ", "_").replace("/", "-")
                    st.download_button(
                        label="⬇️ Unduh Lagu Cover Siap Upload (MP3)",
                        data=buffer_keluar,
                        file_name=nama_file_rapi,
                        mime="audio/mp3"
                    )
                except Exception as err:
                    st.error(f"Gagal melakukan mixing audio: {err}")
