import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CUSTOM CSS MODERN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    .login-box {
        background: white; padding: 40px; border-radius: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0; text-align: center;
    }
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.2rem; text-align: center; margin-bottom: 25px;
    }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #10b981;
    }
    div.stButton > button:first-child { border-radius: 12px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 3. SISTEM DATABASE CSV
FILES = {
    "pasien": "data_pasien.csv",
    "stok": "data_stok.csv",
    "kegiatan": "data_kegiatan.csv",
    "siswa": "db_siswa.csv"
}

def load_data(key, cols):
    if os.path.exists(FILES[key]):
        return pd.read_csv(FILES[key])
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def get_list_kelas():
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))]
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))]
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))]
    return kx + kxi + kxii

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 1.8, 1])
    with col_log:
        st.write("###")
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        l1, l2 = st.columns(2)
        with l1: st.image("logo_sekolah.png", width=70)
        with l2: st.image("logo_uks.png", width=70)
        st.markdown("<h2 style='color:#064e3b; margin-top:10px;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; margin-bottom:25px;'>Sistem Manajemen UKS Digital</p>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="adminuks")
        pw = st.text_input("Password", type="password", placeholder="man1sukabumi")
        if st.button("Masuk ke Sistem", use_container_width=True):
            if user == "adminuks" and pw == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Username atau Password salah.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # 5. SIDEBAR
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_uks.png", width=80)
        st.markdown("<h3 style='color:#064e3b;'>MENU UKS</h3></div>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Navigasi Utama:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan UKS", "📥 Ekspor Data"])
        st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # 6. KONTEN
    if menu == "📊 Dashboard":
        st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><h5>Total Pasien</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h5>Varian Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h5>Status</h5><h2 style="color:#10b981;">Aktif</h2></div>', unsafe_allow_html=True)
        st.markdown("### 🕒 Riwayat Kunjungan")
        st.dataframe(df_p.tail(10), use_container_width=True)

    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>Catat Kunjungan</h1>", unsafe_allow_html=True)
        df_s = load_data("siswa", ["nama_siswa", "kelas"])
        with st.expander("➕ Tambah Master Data Siswa"):
            with st.form("add_siswa", clear_on_submit=True):
                ns = st.text_input("Nama Siswa")
                ks = st.selectbox("Kelas", get_list_kelas(), key="kls_add")
                if st.form_submit_button("Simpan Siswa"):
                    if ns:
                        df_s = pd.concat([df_s, pd.DataFrame([[ns, ks]], columns=["nama_siswa", "kelas"])], ignore_index=True)
                        save_data(df_s, "siswa")
