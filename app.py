import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UKS MAN 1 KOTA SUKABUMI", layout="wide", page_icon="🏥")

# --- 2. STYLE CSS (HIJAU MAN 1) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E0E0E0; }
    
    /* Header Container */
    .header-box {
        display: flex;
        align-items: center;
        background-color: #f0f7f0;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #007A00;
        margin-bottom: 30px;
    }
    
    .title-text {
        margin-left: 20px;
        color: #007A00;
    }

    /* Button & Metrics */
    .stButton>button { background-color: #007A00; color: white; border-radius: 8px; width: 100%; border:none; }
    [data-testid="stMetric"] { background-color: #FFFFFF; border-top: 5px solid #007A00; padding: 15px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    h1, h2, h3 { color: #007A00 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI DATABASE CSV ---
def load_csv(file_name, columns):
    if os.path.exists(file_name):
        return pd.read_csv(file_name)
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_name, index=False)
        return df

# Load data awal
df_pasien = load_csv("data_pasien.csv", ["Tanggal", "Nama", "Kelas", "Keluhan", "Obat"])
df_obat = load_csv("data_obat.csv", ["Obat", "Stok", "Satuan"])
df_kegiatan = load_csv("data_kegiatan.csv", ["Tanggal", "Nama Kegiatan", "Lokasi", "Jumlah Peserta"])

# --- 4. SISTEM LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        try: st.image("logo_uks.png", width=100)
        except: st.warning("Logo UKS tidak ditemukan")
        st.title("Login UKS")
        st.info("MAN 1 KOTA SUKABUMI")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if u == "admin" and p == "uks123":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Akses Ditolak!")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    col_side1, col_side2 = st.columns([1, 3])
    with col_side1:
        try: st.image("logo_sekolah.png", width=50)
        except: st.write("🏫")
    with col_side2:
        st.markdown("**MAN 1 KOTA SUKABUMI**")
    
    st.divider()
    menu = st.radio("MENU", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    st.divider()
    if st.button("Keluar"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. DASHBOARD ---
if menu == "📊 Dashboard":
    # Header dengan Logo PNG
    col_h1, col_h2 = st.columns([1, 8])
    with col_h1:
        try: st.image("logo_uks.png", width=80)
        except: st.write("🏥")
    with col_h2:
        st.title("SISTEM INFORMASI UKS DIGITAL")
        st.subheader("MAN 1 KOTA SUKABUMI")

    st.markdown("---")
    
    # Metrik
    c1, c2, c3 = st.columns(3)
    c1.metric("Pasien Tercatat", len(df_pasien))
    c2.metric("Kegiatan UKS", len(df_kegiatan))
    c3.metric("Jenis Obat", len(df_obat))

    st.divider()
    
    col_grafik, col_tabel = st.columns([2, 1])
    with col_grafik:
        st.subheader("📈 Tren Kunjungan")
        if not df_pasien.empty:
            fig = px.line(df_pasien, x='Tanggal', title="Grafik Pasien", color_discrete_sequence=['#007A00'])
            st.plotly_chart(fig, use_container_width=True)
    with col_tabel:
        st.subheader("📋 Agenda Terbaru")
        st.table(df_kegiatan[['Nama Kegiatan', 'Tanggal']].tail(5))

# --- 7. INPUT PASIEN ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Pencatatan Pasien")
    with st.form("form_p", clear_on_submit=True):
        t = st.date_input("Tanggal")
        n = st.text_input("Nama Siswa")
        k = st.selectbox("Kelas", ["X", "XI", "XII"])
        kl = st.text_area("Keluhan")
        o_list = df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"]
        o = st.selectbox("Obat", o_list)
        
        if st.form_submit_button("Simpan Data"):
            new_row = pd.DataFrame([[t, n, k, kl, o]], columns=df_pasien.columns)
            updated_df = pd.concat([df_pasien, new_row], ignore_index=True)
            updated_df.to_csv("data_pasien.csv", index=False)
            st.success("Data Berhasil Disimpan di Lokal!")
            st.balloons()

# --- 8. STOK OBAT ---
elif menu == "💊 Stok Obat":
    st.title("💊 Inventaris Obat")
    st.dataframe(df_obat, use_container_width=True, hide_index=True)
