import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS MODERN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    .metric-card {
    background: white; padding: 24px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-bottom: 5px solid #10b981; text-align: center;

    }
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.3rem; margin: 0;
    }
   
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE CSV
FILES = {"pasien": "data_pasien.csv", "stok": "data_stok.csv", "kegiatan": "data_kegiatan.csv", "siswa": "db_siswa.csv"}

def load_data(key, cols):
    if os.path.exists(FILES[key]):
        try: return pd.read_csv(FILES[key])
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def get_list_kelas():
    return [f"{tk}-{chr(i)}" for tk in ["X", "XI", "XII"] for i in range(ord('A'), ord('K'))]

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("logo_uks.png", width=120) 
        st.markdown("<h2 style='color:#064e3b;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="Username")
        pw = st.text_input("Password", type="password", placeholder="password")
        if st.button("MASUK", use_container_width=True):
            if user == "adminuks" and pw == "123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Salah!")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=85) 
        st.markdown("<h4>MAN 1 KOTA SUKABUMI</h4></div>", unsafe_allow_html=True)
        menu = st.radio("Menu:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])
        if st.button("🚪 Keluar"):
            st.session_state.auth = False
            st.rerun()

    # 6. KONTEN (PASTIKAN INDENTASI DI SINI SAMA)
    if menu == "📊 Dashboard":
        h_c1, h_c2 = st.columns([0.1, 0.9])
        with h_c1: st.image("logo_uks.png", width=100)
        with h_c2: st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
        
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        df_k = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta"])
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><h5>Kunjungan</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><h5>Kegiatan</h5><h2>{len(df_k)}</h2></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><h5>Jenis Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        
        col_g, col_a = st.columns([1.2, 0.8])
        with col_g:
            st.markdown("### 📈 Statistik Kunjungan")
            if not df_p.empty:
                df_p['Waktu'] = pd.to_datetime(df_p['Waktu']).dt.date
                st.area_chart(df_p.groupby('Waktu').size(), color="#10b981")
        with col_a:
            st.markdown("### 📅 Agenda")
            st.dataframe(df_k.tail(5), use_container_width=True)

    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>Input Pasien</h1>", unsafe_allow_html=True)
        df_s = load_data("siswa", ["nama_siswa", "kelas"])
        with st.expander("➕Tambah Data Siswa"):
            with st.form("f_s"):
                ns = st.text_input("Nama"); ks = st.selectbox("Kelas", get_list_kelas())
                if st.form_submit_button("Simpan"):
                    df_s = pd.concat([df_s, pd.DataFrame([[ns, ks]], columns=df_s.columns)], ignore_index=True)
                    save_data(df_s, "siswa"); st.rerun()
        
        with st.form("f_p"):
            kls = st.selectbox("Kelas", get_list_kelas())
            list_n = df_s[df_s['kelas'] == kls]['nama_siswa'].tolist()
            nama = st.selectbox("Nama", sorted(list_n) if list_n else ["Kosong"])
            kel = st.text_area("Keluhan"); tin = st.text_input("Tindakan")
            if st.form_submit_button("Simpan Kunjungan"):
                df = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
                new = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), nama, kls, kel, tin]], columns=df.columns)
                save_data(pd.concat([df, new], ignore_index=True), "pasien"); st.success("Selesai!")

    elif menu == "💊 Stok Obat":
        st.markdown("<h1 class='main-header'>Stok Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        with st.form("f_o"):
            o_n = st.text_input("Obat"); o_s = st.number_input("Jumlah", 0); o_u = st.selectbox("Satuan", ["Tablet", "Strip", "Pcs", "Botol", "Tube", "Sachet", "Kapsul", "Kaplet", "Pot", "Box", "Blister", "mL", "Unit"])
            if st.form_submit_button("Update"):
                df_o = pd.concat([df_o, pd.DataFrame([[o_n, o_s, o_u]], columns=df_o.columns)], ignore_index=True)
                save_data(df_o, "stok"); st.rerun()
        st.dataframe(df_o, use_container_width=True)

    elif menu == "📅 Kegiatan":
        st.markdown("<h1 class='main-header'>Kegiatan</h1>", unsafe_allow_html=True)
        with st.form("f_k"):
            tgl = st.date_input("Tanggal"); keg = st.text_input("Acara"); pes = st.number_input("Peserta", 0)
            if st.form_submit_button("Simpan"):
                df = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta"])
                new = pd.DataFrame([[str(tgl), keg, pes]], columns=df.columns)
                save_data(pd.concat([df, new], ignore_index=True), "kegiatan"); st.rerun()

    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>Hapus Data</h1>", unsafe_allow_html=True)
        for k in ["pasien", "stok", "kegiatan"]:
            d = load_data(k, [])
            if not d.empty:
                st.write(f"Data {k}")
                idx = st.selectbox(f"Pilih baris {k}", d.index)
                if st.button(f"Hapus {k}"):
                    save_data(d.drop(idx), k); st.rerun()
                st.dataframe(d)

st.markdown("---")
st.caption("© 2026 UKS MAN 1 Kota Sukabumi")
