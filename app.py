import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. STYLE CSS MODERN (Glassmorphism & Clean UI)
st.markdown("""
    <style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Background Utama */
    .stApp { background-color: #f8fafc; }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Tombol Navigasi di Sidebar */
    .stRadio > div { gap: 10px; }
    
    /* Login Card */
    .login-box {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
    }

    /* Container Logo */
    .logo-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 20px;
    }

    /* Header Berwarna Hijau Modern */
    .main-header {
        background: linear-gradient(90deg, #10b981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 30px;
    }

    /* Card untuk Stat/Dashboard */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #10b981;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    /* Custom Button Keluar */
    .stButton > button {
        border-radius: 10px;
        transition: all 0.3s;
    }
    .logout-btn > div > button {
        background-color: #fee2e2 !important;
        color: #ef4444 !important;
        border: 1px solid #fecaca !important;
    }
    .logout-btn > div > button:hover {
        background-color: #ef4444 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATA (CSV)
FILES = {"pasien": "data_pasien.csv", "stok": "data_stok.csv", "kegiatan": "data_kegiatan.csv", "siswa": "db_siswa.csv"}

def load_data(key):
    if os.path.exists(FILES[key]):
        return pd.read_csv(FILES[key])
    return pd.DataFrame()

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        # TAMPILAN LOGO (PERBAIKAN)
        c1, c2 = st.columns(2)
        with c1: st.image("logo_sekolah.png", width=80)
        with c2: st.image("logo_uks.png", width=80)
        
        st.markdown("<h2 style='text-align:center; color:#064e3b;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b;'>Sistem UKS Digital Modern</p>", unsafe_allow_html=True)
        
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk Sekarang →", use_container_width=True):
            if u == "adminuks" and p == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Credential Salah!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR MODERN
    with st.sidebar:
        st.image("logo_uks.png", width=60)
        st.markdown("### UKS Digital")
        st.markdown("---")
        menu = st.radio("Menu Navigasi", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan"])
        
        # TOMBOL KELUAR TERPISAH DI BAWAH
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Keluar Sistem"):
            st.session_state.auth = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 6. KONTEN HALAMAN
    if menu == "📊 Dashboard":
        st.markdown("<h1 class='main-header'>Ringkasan UKS</h1>", unsafe_allow_html=True)
        df_p = load_data("pasien")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><h4>Total Pasien</h4><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="metric-card"><h4>Status Stok</h4><h2>Aman</h2></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="metric-card"><h4>Petugas</h4><h2>Piket</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### Riwayat Terakhir")
        st.table(df_p.tail(5)) if not df_p.empty else st.info("Belum ada data")

    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>Catat Pasien</h1>", unsafe_allow_html=True)
        df_siswa = load_data("siswa")
        
        with st.container():
            with st.form("input_form"):
                nama = st.text_input("Nama Siswa")
                keluhan = st.text_area("Keluhan")
                tindakan = st.text_input("Tindakan")
                if st.form_submit_button("Simpan Data"):
                    # Logika simpan CSV...
                    st.success("Tersimpan!")

    # Menu Stok dan Kegiatan tetap menggunakan logika CSV sebelumnya...
    # (Singkatnya: Gunakan fungsi load_data & save_data)
