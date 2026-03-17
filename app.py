import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UKS MAN 1 KOTA SUKABUMI", layout="wide", page_icon="🏥")

# --- 2. STYLE CSS (PAKSA TERANG & WARNA TETAP) ---
st.markdown("""
    <style>
    /* Paksa background putih dan teks hitam untuk lawan Dark Mode HP */
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E0E0E0; }
    
    /* Warna Teks Global */
    h1, h2, h3, p, span, label, .stMarkdown { color: #007A00 !important; }
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        color: #000000 !important;
        background-color: #FFFFFF !important;
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
    
    /* Header Box */
    .header-box {
        display: flex; align-items: center; background-color: #f0f7f0 !important;
        padding: 20px; border-radius: 15px; border-left: 10px solid #007A00; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEM LOGIN (ANTI-LOGOUT VIA URL) ---
# Mengambil status login dari URL jika ada
if "login" in st.query_params:
    st.session_state.auth_status = True

if 'auth_status' not in st.session_state:
    st.session_state.auth_status = False

def login():
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        if os.path.exists("logo_uks.png"):
            st.image("logo_uks.png", width=100)
        st.title("Login UKS")
        st.write("MAN 1 KOTA SUKABUMI")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if user == "admin" and pwd == "uks123":
                st.session_state.auth_status = True
                # Simpan status ke URL agar saat reload tetap login
                st.query_params["login"] = "true"
                st.rerun()
            else:
                st.error("Username atau Password salah")

def logout():
    st.session_state.auth_status = False
    st.query_params.clear() # Hapus status di URL
    st.rerun()

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
    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        if os.path.exists("logo_sekolah.png"): st.image("logo_sekolah.png", width=50)
    with col_s2:
        st.markdown("**MAN 1 KOTA SUKABUMI**")
    
    st.divider()
    menu = st.radio("MENU", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    st.divider()
    if st.button("Keluar / Logout"):
        logout()

# --- 6. ISI HALAMAN (DASHBOARD) ---
if menu == "📊 Dashboard":
    st.markdown(f"""<div class="header-box">
    <div style="margin-left:10px;"><h2 style="margin:0;">SISTEM UKS DIGITAL</h2>
    <p style="margin:0; color:#444 !important;">MAN 1 KOTA SUKABUMI</p></div></div>""", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Pasien", len(df_pasien))
    c2.metric("Kegiatan", len(df_kegiatan))
    c3.metric("Stok Obat", len(df_obat))

    st.divider()
    col_g, col_t = st.columns([2, 1])
    with col_g:
        st.subheader("📈 Tren Kunjungan")
        if not df_pasien.empty:
            fig = px.area(df_pasien, x='Tanggal', color_discrete_sequence=['#007A00'])
            st.plotly_chart(fig, use_container_width=True)
    with col_t:
        st.subheader("📋 Agenda")
        st.dataframe(df_kegiatan.tail(5), hide_index=True)

# --- 7. INPUT DATA PASIEN ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Input Pasien")
    with st.form("f_pasien", clear_on_submit=True):
        t = st.date_input("Tanggal")
        n = st.text_input("Nama")
        k = st.selectbox("Kelas", ["X", "XI", "XII"])
        kl = st.text_area("Keluhan")
        o = st.selectbox("Obat", df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"])
        if st.form_submit_button("Simpan"):
            new = pd.DataFrame([[t, n, k, kl, o]], columns=df_pasien.columns)
            pd.concat([df_pasien, new], ignore_index=True).to_csv("data_pasien.csv", index=False)
            st.success("Tersimpan!")
            st.rerun()

# --- 8. INPUT KEGIATAN ---
elif menu == "📅 Laporan Kegiatan":
    st.title("📅 Laporan Kegiatan")
    with st.form("f_keg", clear_on_submit=True):
        t_k = st.date_input("Tanggal")
        n_k = st.text_input("Kegiatan")
        l_k = st.text_input("Lokasi")
        p_k = st.number_input("Peserta", min_value=0)
        if st.form_submit_button("Simpan Kegiatan"):
            new_k = pd.DataFrame([[t_k, n_k, l_k, p_k]], columns=df_kegiatan.columns)
            pd.concat([df_kegiatan, new_k], ignore_index=True).to_csv("data_kegiatan.csv", index=False)
            st.success("Kegiatan Dicatat!")
            st.rerun()

# --- 9. STOK OBAT ---
else:
    st.title("💊 Inventaris Obat")
    st.dataframe(df_obat, use_container_width=True, hide_index=True)
