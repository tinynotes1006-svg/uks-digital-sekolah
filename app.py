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
    .header-box {
        display: flex; align-items: center; background-color: #f0f7f0;
        padding: 20px; border-radius: 15px; border-left: 10px solid #007A00; margin-bottom: 30px;
    }
    .stButton>button { background-color: #007A00 !important; color: white !important; border-radius: 8px; width: 100%; border:none; height: 45px; font-weight: bold; }
    [data-testid="stMetric"] { background-color: #FFFFFF; border-top: 5px solid #007A00; padding: 15px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    h1, h2, h3 { color: #007A00 !important; }
    .stDownloadButton>button { background-color: #2E7D32 !important; color: white !important; }
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

# Inisialisasi Data
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
        except: st.info("🏥 Logo UKS")
        st.title("Login UKS")
        st.write("MAN 1 KOTA SUKABUMI")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if u == "adminuks" and p == "uks12345":
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
    menu = st.radio("MENU UTAMA", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    st.divider()
    if st.button("Keluar"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. DASHBOARD ---
if menu == "📊 Dashboard":
    st.markdown(f"""<div class="header-box"><img src="https://upload.wikimedia.org/wikipedia/commons/b/bd/Logo_UKS.png" width="70">
    <div style="margin-left:20px;"><h2 style="margin:0;">SISTEM UKS DIGITAL</h2><p style="margin:0; color:#555;">MAN 1 KOTA SUKABUMI</p></div></div>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Pasien Tercatat", len(df_pasien))
    c2.metric("Kegiatan UKS", len(df_kegiatan))
    c3.metric("Jenis Obat", len(df_obat))

    st.divider()
    col_grafik, col_tabel = st.columns([2, 1])
    with col_grafik:
        st.subheader("📈 Tren Kunjungan")
        if not df_pasien.empty:
            fig = px.area(df_pasien, x='Tanggal', title="Grafik Kunjungan", color_discrete_sequence=['#007A00'])
            st.plotly_chart(fig, use_container_width=True)
    with col_tabel:
        st.subheader("📋 Agenda Terbaru")
        st.dataframe(df_kegiatan[['Nama Kegiatan', 'Tanggal']].tail(5), hide_index=True)

    # TOMBOL DOWNLOAD BACKUP
    st.divider()
    st.subheader("📥 Backup Data (Download CSV)")
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download Data Pasien", df_pasien.to_csv(index=False), "backup_pasien.csv", "text/csv")
    d2.download_button("Download Data Kegiatan", df_kegiatan.to_csv(index=False), "backup_kegiatan.csv", "text/csv")
    d3.download_button("Download Data Obat", df_obat.to_csv(index=False), "backup_obat.csv", "text/csv")

# --- 7. INPUT PASIEN ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Input Pasien Baru")
    with st.form("form_pasien", clear_on_submit=True):
        t = st.date_input("Tanggal")
        n = st.text_input("Nama Siswa")
        k = st.selectbox("Kelas", ["X", "XI", "XII"])
        kl = st.text_area("Keluhan")
        o_list = df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"]
        o = st.selectbox("Obat", o_list)
        if st.form_submit_button("Simpan Data Pasien"):
            new_data = pd.DataFrame([[t, n, k, kl, o]], columns=df_pasien.columns)
            pd.concat([df_pasien, new_data], ignore_index=True).to_csv("data_pasien.csv", index=False)
            st.success(f"Data {n} berhasil disimpan!")
            st.balloons()

# --- 8. LAPORAN KEGIATAN ---
elif menu == "📅 Laporan Kegiatan":
    st.title("📅 Input Laporan Kegiatan")
    with st.form("form_kegiatan", clear_on_submit=True):
        tgl_k = st.date_input("Tanggal Pelaksanaan")
        nama_k = st.text_input("Nama Kegiatan")
        lokasi = st.text_input("Lokasi")
        peserta = st.number_input("Jumlah Peserta", min_value=0)
        if st.form_submit_button("Simpan Laporan Kegiatan"):
            new_keg = pd.DataFrame([[tgl_k, nama_k, lokasi, peserta]], columns=df_kegiatan.columns)
            pd.concat([df_kegiatan, new_keg], ignore_index=True).to_csv("data_kegiatan.csv", index=False)
            st.success(f"Kegiatan '{nama_k}' berhasil dicatat!")

# --- 9. STOK OBAT ---
else:
    st.title("💊 Inventaris Obat")
    st.dataframe(df_obat, use_container_width=True, hide_index=True)
    with st.expander("Update Stok Obat"):
        st.info("Untuk menambah/mengubah daftar obat, silakan download file CSV di Dashboard, edit di Excel, lalu upload kembali ke GitHub.")
