import streamlit as st

st.set_page_config(
    page_title="Suno AI Lyric & Style Formatter",
    page_icon="🎵",
    layout="wide"
)

st.title("🎛️ Formatter Lirik & Generator Style untuk Suno AI")
st.caption("Tempel lirik lagu, tentukan style genre, lalu klik tombol untuk mengonversinya ke format baku Suno.")

# Inisialisasi State
if "lirik_terformat" not in st.session_state:
    st.session_state["lirik_terformat"] = ""
if "style_hasil" not in st.session_state:
    st.session_state["style_hasil"] = ""
if "exclude_hasil" not in st.session_state:
    st.session_state["exclude_hasil"] = ""
if "judul_yt" not in st.session_state:
    st.session_state["judul_yt"] = ""

# --- FUNGSI FORMAT LIRIK OTOMATIS KE STRUKTUR SUNO ---
def format_ke_suno(teks_mentah, genre_list):
    baris_list = [b.strip() for b in teks_mentah.split("\n") if b.strip()]
    if not baris_list:
        return "[Intro]\n[Instrumental]\n\n[Verse]\n\n[Chorus]\n\n[Outro]"
    
    total = len(baris_list)
    pembagian = max(1, total // 4)
    
    bagian1 = "\n".join(baris_list[:pembagian])
    bagian2 = "\n".join(baris_list[pembagian : pembagian * 2])
    bagian3 = "\n".join(baris_list[pembagian * 2 : pembagian * 3])
    bagian4 = "\n".join(baris_list[pembagian * 3 :])
    
    # Deteksi drop instrumen khusus genre
    tag_drop = "[Drop Bass Glerr]" if any("Horeg" in g for g in genre_list) else "[Guitar Solo]"
    
    lirik_suno = (
        f"[Intro]\n"
        f"[Instrumental Build-up]\n\n"
        f"[Verse 1]\n{bagian1}\n\n"
        f"[Pre-Chorus]\n{bagian2}\n\n"
        f"[Chorus]\n{bagian3}\n\n"
        f"{tag_drop}\n\n"
        f"[Verse 2]\n{bagian4}\n\n"
        f"[Chorus]\n{bagian3}\n\n"
        f"[Outro]\n[Fade Out]"
    )
    return lirik_suno


# --- TAMPILAN INPUT UTAMA ---
col_in1, col_in2 = st.columns([1, 1])

with col_in1:
    st.subheader("1. Masukkan Informasi & Lirik Mentah")
    judul_input = st.text_input("Judul Lagu Asli:", placeholder="Contoh: Di Bukit Berbunga")
    artis_input = st.text_input("Penyanyi / Artis Asli:", placeholder="Contoh: Uci Bing Slamet")
    
    lirik_mentah = st.text_area(
        "Tempel Lirik Mentah (Bisa lirik biasa tanpa tag):",
        height=260,
        placeholder="Tempel teks lirik lagu di sini..."
    )

with col_in2:
    st.subheader("2. Tentukan Racikan Style & Karakter")
    
    genre_opsi = st.multiselect(
        "Pilih Komponen Genre (Bisa lebih dari 1):",
        options=[
            "Indonesian DJ Horeg", "Sub-bass Glerr 30Hz", "Dangdut Koplo",
            "Kendang Rampak", "Heavy Metal", "Distorted Heavy Guitar",
            "Mistis Etnik Gamelan Horor", "Dark Ambient Supranatural",
            "Rock", "EDM Dutch Trap", "Breakbeat", "Jedag Jedug"
        ],
        default=["Indonesian DJ Horeg", "Sub-bass Glerr 30Hz", "Dangdut Koplo"]
    )
    
    karakter_vokal = st.selectbox(
        "Karakter Vokal:",
        [
            "Energetic Male Vocal", 
            "Powerful Female Vocal", 
            "Heavy Metal Growl / Scream", 
            "Sinden Mystical Female Vocal", 
            "Raw Indonesian Vocal"
        ]
    )
    
    tempo = st.select_slider(
        "Tempo Ketukan:",
        options=["Slow / Dark (85-95 BPM)", "Medium Beat (115-125 BPM)", "Fast / Horeg (135-145 BPM)"],
        value="Fast / Horeg (135-145 BPM)"
    )

# --- TOMBOL GENERATE FORMAT ---
if st.button("⚡ Formatkan Lirik & Siapkan Style untuk Suno AI", type="primary"):
    if not lirik_mentah.strip():
        st.warning("Silakan tempelkan lirik lagu terlebih dahulu di kolom kiri.")
    else:
        # Format lirik
        st.session_state["lirik_terformat"] = format_ke_suno(lirik_mentah, genre_opsi)
        
        # Susun Style of Music
        style_teks = f"{', '.join(genre_opsi)}, {karakter_vokal}, {tempo}, punchy beat, high clarity, dynamic mastering"
        st.session_state["style_hasil"] = style_teks
        
        # Susun Exclude Style (Negatif prompt agar Suno tidak membuat gaya yang salah)
        exclude_teks = "slow tempo, lo-fi, acoustic piano, acoustic guitar, quiet, soft voice, monotone, bad quality, noisy"
        st.session_state["exclude_hasil"] = exclude_teks
        
        # Judul untuk YouTube
        genre_label = " x ".join(genre_opsi[:2]) if genre_opsi else "Remix"
        st.session_state["judul_yt"] = f"{judul_input or 'Lagu'} - {artis_input or 'Artis'} (AI Cover {genre_label})"
        
        st.success("Format Suno berhasil dibuat! Silakan salin data di bawah ini.")

st.divider()

# --- TAMPILAN OUTPUT HASIL (TINGGAL SALIN KE SUNO) ---
if st.session_state["lirik_terformat"]:
    st.subheader("3. Hasil Siap Salin ke Suno AI")
    
    out_col1, out_col2 = st.columns(2)
    
    with out_col1:
        st.write("**A. Salin ke Kolom 'Lyrics' di Suno:**")
        st.text_area("Format Lirik + Metatag:", value=st.session_state["lirik_terformat"], height=320)
    
    with out_col2:
        st.write("**B. Salin ke Kolom 'Style of Music' di Suno:**")
        st.code(st.session_state["style_hasil"], language="text")
        
        st.write("**C. Salin ke Kolom 'Exclude Styles' di Suno:**")
        st.code(st.session_state["exclude_hasil"], language="text")
        
        st.write("**D. Rekomendasi Judul Video YouTube:**")
        st.code(st.session_state["judul_yt"], language="text")
        
    st.link_button(
        "🚀 Buka Suno AI (Tinggal Paste & Klik Create)",
        "https://suno.com/create",
        type="primary"
    )
