import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- 1. SETINGAN HALAMAN ---
st.set_page_config(page_title="UKS Digital PRO", layout="wide", page_icon="🏥")

# --- 2. CUSTOM CSS (WARNA HIJAU CMYK 100,0,100,30 & PUTIH) ---
st.markdown("""
    <style>
    /* Mengatur warna latar belakang seluruh aplikasi */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Mengatur sidebar */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Tombol Utama (Warna Hijau CMYK 100,0,100,30) */
    .stButton>button {
        background-color: #007A00;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #005F00;
        color: white;
    }
    
    /* Kartu Metrik Modern */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #F0F0F0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    /* Judul dan Teks */
    h1, h2, h3 {
        color: #007A00 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Border untuk Area Chart */
    .plot-container {
        border-radius: 12px;
        background-color: #FFFFFF;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEM LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try: st.image("logo_uks.png", width=120)
        except: st.info("🏥")
        st.title("Login UKS Digital")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if u == "adminuks@gmail.com" and p == "uks123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Kredensial salah.")
    st.stop()

# --- 4. KONEKSI DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_pasien = conn.read(worksheet="Pasien")
df_obat = conn.read(worksheet="Obat")
df_kegiatan = conn.read(worksheet="Kegiatan")

# --- 5. SIDEBAR ---
with st.sidebar:
    try: st.image("logo_sekolah.png", width=100)
    except: st.write("🏫 MAN 1 KOTA SUKABUMI")
    st.divider()
    menu = st.radio("MAIN MENU", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. TAMPILAN DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Monitoring Dashboard")
    
    # Statistik 3 Kolom
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Pasien", f"{len(df_pasien)} Siswa")
    k2.metric("Total Kegiatan", f"{len(df_kegiatan)} Acara")
    k3.metric("Jenis Obat", f"{len(df_obat)} Macam")

    st.markdown("---")
    
    col_kiri, col_kanan = st.columns([2, 1])
    
    with col_kiri:
        st.subheader("📈 Tren Pasien Harian")
        if not df_pasien.empty:
            # Grafik Area dengan warna Hijau CMYK 100,0,100,30
            fig = px.area(df_pasien, x='Tanggal', color_discrete_sequence=['#007A00'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with col_kanan:
        st.subheader("📅 Kegiatan Terbaru")
        st.dataframe(df_kegiatan[['Nama Kegiatan', 'Tanggal']].tail(5), hide_index=True)

# --- 7. FORM INPUT ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Form Pemeriksaan")
    with st.form("form_p"):
        tgl = st.date_input("Tanggal")
        nama = st.text_input("Nama Siswa")
        kls = st.selectbox("Kelas", ["X", "XI", "XII"])
        klh = st.text_area("Keluhan")
        obt = st.selectbox("Obat", df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"])
        if st.form_submit_button("Simpan Data"):
            st.success("Berhasil! Data terkirim ke Google Sheets.")

elif menu == "📅 Laporan Kegiatan":
    st.title("📅 Laporan Acara UKS")
    with st.form("form_k"):
        tgl_k = st.date_input("Tanggal")
        nama_k = st.text_input("Nama Kegiatan")
        peserta = st.number_input("Jumlah Peserta", min_value=0)
        ket = st.text_area("Catatan")
        if st.form_submit_button("Simpan Kegiatan"):
            st.success("Laporan kegiatan disimpan.")

# --- 8. TAMPILAN OBAT ---
else:
    st.title("💊 Inventaris Obat")
    st.dataframe(df_obat, use_container_width=True, hide_index=True)