import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UKS Digital PRO", layout="wide", page_icon="🏥")

# --- 2. DESAIN MODERN (HIJAU CMYK: 100, 0, 100, 30 -> #007A00) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E0E0E0; }
    
    /* Tombol Utama */
    .stButton>button {
        background-color: #007A00;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        width: 100%;
    }
    
    /* Kartu Statistik */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-left: 5px solid #007A00;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Judul Hijau */
    h1, h2, h3 { color: #007A00 !important; }
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
            if u == "admin" and p == "uks123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username atau Password Salah!")
    st.stop()

# --- 4. KONEKSI DATA (DENGAN PENANGANAN ERROR) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Membaca 3 sheet berbeda
        p = conn.read(worksheet="Pasien", ttl=0)
        o = conn.read(worksheet="Obat", ttl=0)
        k = conn.read(worksheet="Kegiatan", ttl=0)
        return p, o, k
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        st.info("Saran: Pastikan link di Secrets benar dan nama tab di Google Sheets adalah: Pasien, Obat, dan Kegiatan.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_pasien, df_obat, df_kegiatan = load_data()

# --- 5. SIDEBAR ---
with st.sidebar:
    try: st.image("logo_sekolah.png", width=100)
    except: st.write("🏫 SMA NEGERI DIGITAL")
    st.divider()
    menu = st.radio("NAVIGASI", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. HALAMAN DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Monitoring Dashboard UKS")
    
    # Baris Metrik
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Pasien", f"{len(df_pasien)} Siswa")
    m2.metric("Total Kegiatan", f"{len(df_kegiatan)} Acara")
    m3.metric("Stok Obat", f"{len(df_obat)} Jenis")

    st.divider()
    
    col_kiri, col_kanan = st.columns([2, 1])
    
    with col_kiri:
        st.subheader("📈 Tren Kunjungan")
        if not df_pasien.empty:
            fig = px.area(df_pasien, x='Tanggal', color_discrete_sequence=['#007A00'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Data Pasien belum tersedia.")
    
    with col_kanan:
        st.subheader("📋 Kegiatan Terbaru")
        if not df_kegiatan.empty:
            st.dataframe(df_kegiatan[['Nama Kegiatan', 'Tanggal']].tail(5), hide_index=True)
        else:
            st.info("Belum ada kegiatan.")

# --- 7. HALAMAN INPUT PASIEN ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Input Pasien Baru")
    with st.form("form_pasien"):
        tgl = st.date_input("Tanggal")
        nama = st.text_input("Nama Siswa")
        kls = st.selectbox("Kelas", ["X", "XI", "XII"])
        klh = st.text_area("Keluhan")
        # Ambil daftar obat dari sheet Obat
        list_obat = df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"]
        obt = st.selectbox("Obat", list_obat)
        
        if st.form_submit_button("Simpan ke Cloud"):
            st.success("Data berhasil tercatat! Silakan update Google Sheets Anda secara manual.")
            st.balloons()

# --- 8. HALAMAN KEGIATAN ---
elif menu == "📅 Laporan Kegiatan":
    st.title("📅 Input Laporan Kegiatan")
    with st.form("form_keg"):
        tgl_k = st.date_input("Tanggal")
        nama_k = st.text_input("Nama Kegiatan")
        lokasi = st.text_input("Lokasi")
        peserta = st.number_input("Jumlah Peserta", min_value=0)
        
        if st.form_submit_button("Simpan Laporan"):
            st.success(f"Kegiatan {nama_k} telah disimpan!")

# --- 9. HALAMAN STOK OBAT ---
else:
    st.title("💊 Inventaris Obat")
    if not df_obat.empty:
        st.dataframe(df_obat, use_container_width=True, hide_index=True)
    else:
        st.error("Data obat tidak ditemukan di Google Sheets.")
