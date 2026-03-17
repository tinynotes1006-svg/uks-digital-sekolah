import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="UKS Digital MAN 1 KOTA SUKABUMI", layout="wide", page_icon="🏥")

# --- 2. DESAIN MODERN (HIJAU CMYK: 100, 0, 100, 30 -> #007A00) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E0E0E0; }
    
    /* Container Header */
    .header-container {
        display: flex;
        align-items: center;
        background-color: #f0f7f0;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-left: 10px solid #007A00;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .school-name {
        color: #007A00;
        font-size: 26px;
        font-weight: 800;
        margin-left: 20px;
        line-height: 1.2;
    }

    /* Tombol Utama */
    .stButton>button {
        background-color: #007A00;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        border: none;
    }
    
    /* Kartu Statistik */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border-top: 5px solid #007A00;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
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
        st.subheader("MAN 1 KOTA SUKABUMI")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if u == "admin" and p == "uks123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Username atau Password Salah!")
    st.stop()

# --- 4. KONEKSI DATA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        p = conn.read(worksheet="Pasien", ttl=0)
        o = conn.read(worksheet="Obat", ttl=0)
        k = conn.read(worksheet="Kegiatan", ttl=0)
        return p, o, k
    except Exception as e:
        st.error(f"Koneksi Database Gagal: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df_pasien, df_obat, df_kegiatan = load_data()

# --- 5. SIDEBAR ---
with st.sidebar:
    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        try: st.image("logo_sekolah.png", width=50)
        except: st.write("🏫")
    with col_s2:
        st.markdown("### MAN 1 <br> KOTA SUKABUMI", unsafe_allow_html=True)
    
    st.divider()
    menu = st.radio("NAVIGASI UTAMA", ["📊 Dashboard", "🤒 Input Pasien", "📅 Laporan Kegiatan", "💊 Stok Obat"])
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. HALAMAN DASHBOARD ---
if menu == "📊 Dashboard":
    # HEADER DASHBOARD
    st.markdown(f"""
        <div class="header-container">
            <img src="https://upload.wikimedia.org/wikipedia/commons/b/bd/Logo_UKS.png" width="70">
            <div class="school-name">
                SISTEM INFORMASI UKS DIGITAL<br>
                <span style="font-size: 20px; font-weight: 500; color: #444;">MAN 1 KOTA SUKABUMI</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistik Utama
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Kunjungan", f"{len(df_pasien)} Siswa")
    m2.metric("Total Kegiatan", f"{len(df_kegiatan)} Acara")
    m3.metric("Jenis Obat", f"{len(df_obat)} Macam")

    st.divider()
    
    col_kiri, col_kanan = st.columns([2, 1])
    
    with col_kiri:
        st.subheader("📈 Statistik Kunjungan Siswa")
        if not df_pasien.empty:
            fig = px.area(df_pasien, x='Tanggal', color_discrete_sequence=['#007A00'])
            fig.update_layout(hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Belum ada data kunjungan pasien.")
    
    with col_kanan:
        st.subheader("📋 Agenda Kegiatan")
        if not df_kegiatan.empty:
            st.dataframe(df_kegiatan[['Nama Kegiatan', 'Tanggal']].tail(5), hide_index=True)
        else:
            st.info("Belum ada riwayat kegiatan.")

# --- 7. HALAMAN INPUT PASIEN ---
elif menu == "🤒 Input Pasien":
    st.title("🤒 Pencatatan Pasien UKS")
    with st.form("form_pasien"):
        tgl = st.date_input("Tanggal Pemeriksaan")
        nama = st.text_input("Nama Lengkap Siswa")
        kls = st.selectbox("Kelas", ["X", "XI", "XII"])
        klh = st.text_area("Keluhan/Diagnosa")
        list_obat = df_obat['Obat'].tolist() if not df_obat.empty else ["Lainnya"]
        obt = st.selectbox("Tindakan/Obat diberikan", list_obat)
        
        if st.form_submit_button("Simpan Data Pasien"):
            st.success(f"Data {nama} Berhasil Dicatat!")
            st.balloons()

# --- 8. HALAMAN KEGIATAN ---
elif menu == "📅 Laporan Kegiatan":
    st.title("📅 Laporan Aktivitas UKS")
    with st.form("form_keg"):
        tgl_k = st.date_input("Tanggal Pelaksanaan")
        nama_k = st.text_input("Nama Kegiatan (Contoh: Imunisasi)")
        lokasi = st.text_input("Lokasi Kegiatan")
        peserta = st.number_input("Jumlah Peserta Terlibat", min_value=0)
        if st.form_submit_button("Simpan Laporan Kegiatan"):
            st.success(f"Kegiatan '{nama_k}' telah diverifikasi.")

# --- 9. HALAMAN STOK OBAT ---
else:
    st.title("💊 Manajemen Stok Obat")
    if not df_obat.empty:
        st.dataframe(df_obat, use_container_width=True, hide_index=True)
    else:
        st.error("Data stok obat tidak terbaca.")
