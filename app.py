import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UKS MAN 1 KOTA SUKABUMI", layout="wide", page_icon="🏥")

# --- 2. STYLE CSS (WARNA HIJAU & ANTI-DARK MODE) ---
st.markdown("""
    <style>
    /* Paksa Background Putih */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Judul & Teks Utama (Warna Hijau MAN 1) */
    h1, h2, h3, .stMarkdown p { color: #007A00 !important; font-weight: bold; }
    
    /* Label Input */
    label, .stWidget label { color: #333333 !important; font-weight: 600 !important; }

    /* Kotak Header Dashboard */
    .header-box {
        display: flex; 
        align-items: center; 
        background-color: #f0f7f0 !important;
        padding: 30px; 
        border-radius: 15px; 
        border-left: 12px solid #007A00; 
        margin-bottom: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    /* Tombol Utama */
    .stButton>button { 
        background-color: #007A00 !important; 
        color: white !important; 
        border-radius: 8px; 
        height: 45px; 
        font-weight: bold;
        border: none;
    }

    /* Tombol Download */
    .stDownloadButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border-radius: 8px;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEM LOGIN (ANTI-LOGOUT) ---
if "login" in st.query_params:
    st.session_state.auth_status = True
elif 'auth_status' not in st.session_state:
    st.session_state.auth_status = False

def login():
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo_uks.png"):
            st.image("logo_uks.png", width=120)
        st.title("Login UKS")
        st.write("MAN 1 KOTA SUKABUMI")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if user == "admin" and pwd == "uks123":
                st.session_state.auth_status = True
                st.query_params["login"] = "true"
                st.rerun()
            else:
                st.error("Username atau Password salah")

if not st.session_state.auth_status:
    login()
    st.stop()

# --- 4. DATA LOADER ---
def load_csv(file_name, columns):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    return pd.DataFrame(columns=columns)

df_pasien = load_csv("data_pasien.csv", ["Tanggal", "Nama", "Kelas", "Keluhan", "Obat"])
df_obat = load_csv("data_obat.csv", ["Obat", "Stok", "Satuan"])
df_kegiatan = load_csv("data_kegiatan.csv", ["Tanggal", "Nama Kegiatan", "Lokasi", "Jumlah Peserta"])

# --- 5. SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo_sekolah.png"):
        st.image("logo_sekolah.png", width=80)
    st.markdown("### MAN 1 KOTA SUKABUMI")
    st.divider()
    menu = st.radio("NAVIGASI", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    if st.button("Keluar"):
        st.session_state.auth_status = False
        st.query_params.clear()
        st.rerun()

# --- 6. DASHBOARD ---
if menu == "📊 Dashboard":
    # Header dengan Logo
    st.markdown('<div class="header-box">', unsafe_allow_html=True)
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if os.path.exists("logo_uks.png"):
            st.image("logo_uks.png", width=80)
    with col_title:
        st.title("SISTEM UKS DIGITAL")
        st.write("MAN 1 KOTA SUKABUMI")
    st.markdown('</div>', unsafe_allow_html=True)

    # Statistik
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pasien", len(df_pasien))
    m2.metric("Total Kegiatan", len(df_kegiatan))
    m3.metric("Jenis Obat", len(df_obat))

    st.divider()
    cg, ct = st.columns([2, 1])
    with cg:
        st.subheader("📈 Tren Kunjungan")
        if not df_pasien.empty:
            fig = px.area(df_pasien, x='Tanggal', color_discrete_sequence=['#007A00'])
            st.plotly_chart(fig, use_container_width=True)
    with ct:
        st.subheader("📋 Agenda Terbaru")
        st.dataframe(df_kegiatan.tail(5), hide_index=True)

    # SISTEM DOWNLOAD (BACKUP)
    st.divider()
    st.subheader("📥 Download & Backup Data")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("Download Data Pasien", df_pasien.to_csv(index=False), "data_pasien.csv", "text/csv")
    with d2:
        st.download_button("Download Data Kegiatan", df_kegiatan.to_csv(index=False), "data_kegiatan.csv", "text/csv")
    with d3:
        st.download_button("Download Data Obat", df_obat.to_csv(index=False), "data_obat.csv", "text/csv")

# --- 7. INPUT PASIEN ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Input Pasien")
    with st.form("form_p", clear_on_submit=True):
        t = st.date_input("Tanggal")
        n = st.text_input("Nama Lengkap")
        k = st.selectbox("Kelas", ["X", "XI", "XII"])
        kl = st.text_area("Keluhan")
        o = st.selectbox("Obat", df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"])
        if st.form_submit_button("Simpan Data"):
            new = pd.DataFrame([[t, n, k, kl, o]], columns=df_pasien.columns)
            pd.concat([df_pasien, new], ignore_index=True).to_csv("data_pasien.csv", index=False)
            st.success("Data berhasil disimpan!")
            st.rerun()

# --- 8. INPUT KEGIATAN ---
elif menu == "📅 Laporan Kegiatan":
    st.title("📅 Laporan Kegiatan")
    with st.form("form_k", clear_on_submit=True):
        tk = st.date_input("Tanggal")
        nk = st.text_input("Nama Kegiatan")
        lk = st.text_input("Lokasi")
        pk = st.number_input("Jumlah Peserta", min_value=0)
        if st.form_submit_button("Simpan Laporan"):
            newk = pd.DataFrame([[tk, nk, lk, pk]], columns=df_kegiatan.columns)
            pd.concat([df_kegiatan, newk], ignore_index=True).to_csv("data_kegiatan.csv", index=False)
            st.success("Laporan kegiatan tersimpan!")
            st.rerun()

# --- 9. STOK OBAT ---
else:
    st.title("💊 Inventaris Obat")
    st.dataframe(df_obat, use_container_width=True, hide_index=True)
