import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime
import os

# 1. KONFIGURASI HALAMAN & STYLE CSS (HIJAU TERANG MAN 1)
st.set_page_config(page_title="UKS Digital MAN 1 Kota Sukabumi", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    /* Mengatur Container Logo agar Sejajar dan Kecil */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin-bottom: 5px;
    }
    
    /* Ukuran Logo 50px sesuai permintaan */
    .login-logo-img {
        width: 50px;
        height: 50px;
        object-fit: contain;
    }

    /* Warna Sidebar Hijau Tua */
    [data-testid="stSidebar"] { background-color: #004d40; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Tombol Hijau Terang */
    .stButton>button {
        background-color: #00c853; 
        color: white;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
        border: none;
    }
    .stButton>button:hover { background-color: #00e676; border: 1px solid white; }

    /* Styling Teks Login */
    .sekolah-name-login {
        text-align: center;
        color: #1b5e20;
        font-size: 20px;
        font-weight: bold;
        margin-top: 5px;
    }
    .sekolah-sub-login {
        text-align: center;
        color: #43a047;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Styling Form */
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #f1f8e9;
    }
    
    .main-header {
        text-align: center; 
        color: #1b5e20; 
        padding: 5px;
        border-bottom: 2px solid #00c853;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KONEKSI DATABASE (VERSI ANTI-GAGAL) ---
try:
    # Mengambil data langsung dari rahasia (Secrets)
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    
    # Inisialisasi koneksi
    conn = st.connection("supabase", 
                         type=SupabaseConnection,
                         url=s_url, 
                         key=s_key)
except Exception as e:
    st.error("🚨 KONEKSI DATABASE GAGAL!")
    st.info(f"Pesan Error: {e}")
    st.warning("Tips: Pastikan menu Secrets di Streamlit Cloud sudah diisi dengan format [connections.supabase]")
    st.stop()

# 3. FUNGSI HELPER KELAS
def get_kelas_list():
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))]
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))]
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))]
    return kx + kxi + kxii

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.write("") # Spacer
        # Tampilan Logo Berdampingan (Pastikan file ada di GitHub)
        st.markdown("""
            <div class="logo-container">
                <img src="https://raw.githubusercontent.com/krisna-be/uks-digital-sekolah/main/logo_sekolah.png" class="login-logo-img">
                <img src="https://raw.githubusercontent.com/krisna-be/uks-digital-sekolah/main/logo_uks.png" class="login-logo-img">
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='sekolah-name-login'>MAN 1 Kota Sukabumi</div>", unsafe_allow_html=True)
        st.markdown("<div class='sekolah-sub-login'>SISTEM MANAJEMEN UKS DIGITAL</div>", unsafe_allow_html=True)
        
        with st.container():
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("LOGIN"):
                if u == "adminuks" and p == "man1sukabumi":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Akses Ditolak!")
else:
    # 5. SIDEBAR & MENU
    st.sidebar.markdown("<h3 style='text-align:center;'>🏥 UKS MAN 1</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("MENU UTAMA:", 
        ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan Besar", "📊 Laporan", "Keluar"])
    
    if menu == "Keluar":
        st.session_state.auth = False
        st.rerun()

    # AMBIL DATA GLOBAL
    try:
        df_p = pd.DataFrame(conn.table("data_pasien").select("*").execute().data)
        df_o = pd.DataFrame(conn.table("stok_obat").select("*").execute().data)
        df_k = pd.DataFrame(conn.table("kegiatan_uks").select("*").execute().data)
    except:
        df_p = df_o = df_k = pd.DataFrame()

    # --- HALAMAN DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 class='main-header'>📊 RINGKASAN DATA UKS</h2>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Pasien", len(df_p))
        c2.metric("Jenis Obat", len(df_o))
        c3.metric("Kegiatan", len(df_k))
        
        st.markdown("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("⚠️ Stok Obat Kritis (<=10)")
            if not df_o.empty:
                kritis = df_o[df_o['jumlah'] <= 10]
                st.table(kritis) if not kritis.empty else st.success("Stok Aman")
        with col_b:
            st.subheader("🕒 Kunjungan Terbaru")
            if not df_p.empty:
                st.write(df_p.sort_values(by='waktu', ascending=False).head(5)[['nama_siswa','keluhan']])

    # --- HALAMAN INPUT PASIEN ---
    elif menu == "📝 Input Pasien":
        st.markdown("<h2 class='main-header'>📝 CATAT KUNJUNGAN</h2>", unsafe_allow_html=True)
        try:
            siswa_data = pd.DataFrame(conn.table("master_siswa").select("*").execute().data)
        except:
            siswa_data = pd.DataFrame(columns=['nama_siswa', 'kelas'])

        with st.form("input_p"):
            p_kls = st.selectbox("Kelas", get_kelas_list())
            list_nama = siswa_data[siswa_data['kelas'] == p_kls]['nama_siswa'].tolist()
            p_nama = st.selectbox("Nama Siswa", sorted(list_nama) if list_nama else ["Data Siswa Kosong"])
            p_keluhan = st.text_area("Keluhan")
            p_tindakan = st.text_input("Tindakan/Obat")
            p_petugas = st.text_input("Petugas Piket")
            if st.form_submit_button("SIMPAN"):
                if p_nama != "Data Siswa Kosong" and p_keluhan:
                    conn.table("data_pasien").insert({"nama_siswa":p_nama, "kelas":p_kls, "keluhan":p_keluhan, "obat_tindakan":p_tindakan, "petugas":p_petugas}).execute()
                    st.success("Tersimpan!"); st.balloons()
                else: st.error("Lengkapi data!")

    # --- HALAMAN STOK OBAT ---
    elif menu == "💊 Stok Obat":
        st.markdown("<h2 class='main-header'>💊 STOK OBAT</h2>", unsafe_allow_html=True)
        with st.form("stok_o"):
            n_o = st.text_input("Nama Obat")
            j_o = st.number_input("Jumlah", min_value=0)
            s_o = st.selectbox("Satuan", ["Tablet", "Botol", "Pcs", "Sachet"])
            if st.form_submit_button("UPDATE"):
                conn.table("stok_obat").upsert({"nama_obat":n_o, "jumlah":j_o, "satuan":s_o}).execute()
                st.success("Stok diperbarui!")
        st.dataframe(df_o, use_container_width=True)

    # --- HALAMAN KEGIATAN ---
    elif menu == "📅 Kegiatan Besar":
        st.markdown("<h2 class='main-header'>📅 KEGIATAN KHUSUS</h2>", unsafe_allow_html=True)
        with st.form("keg_b"):
            t_k = st.date_input("Tanggal")
            n_k = st.text_input("Nama Kegiatan")
            l_k = st.text_input("Lokasi")
            p_k = st.number_input("Peserta", min_value=0)
            if st.form_submit_button("SIMPAN KEGIATAN"):
                conn.table("kegiatan_uks").insert({"tanggal":str(t_k), "nama_kegiatan":n_k, "lokasi":l_k, "jumlah_peserta":p_k}).execute()
                st.success("Berhasil!")

    # --- HALAMAN LAPORAN ---
    elif menu == "📊 Laporan":
        st.markdown("<h2 class='main-header'>📊 DOWNLOAD LAPORAN</h2>", unsafe_allow_html=True)
        if not df_p.empty:
            st.download_button("📥 Download Laporan Pasien (CSV)", df_p.to_csv(index=False), "laporan_pasien.csv")
            st.dataframe(df_p)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi")
