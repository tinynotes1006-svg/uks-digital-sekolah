import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime
import os

# 1. KONFIGURASI HALAMAN & STYLE CSS (HIJAU MAN 1)
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #004d40; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
    .stButton>button:hover { background-color: #1b5e20; color: white; border: 1px solid #a5d6a7; }
    .stForm { border: 1px solid #e0e0e0; border-radius: 10px; padding: 20px; background-color: #f1f8e9; }
    .main-header {
        text-align: center; 
        color: #2e7d32; 
        padding: 10px;
        border-bottom: 3px solid #2e7d32;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# CARA KONEKSI BARU (LEBIH KUAT)
try:
    # Mengambil kredensial langsung dari st.secrets
    supabase_url = st.secrets["connections"]["supabase"]["url"]
    supabase_key = st.secrets["connections"]["supabase"]["key"]
    
    # Koneksi manual menggunakan st.connection
    conn = st.connection("supabase", 
                         type=SupabaseConnection, 
                         url=supabase_url, 
                         key=supabase_key)
except Exception as e:
    st.error(f"🚨 KONEKSI MASIH GAGAL: {e}")
    st.info("Tips: Pastikan di Secrets tulisannya [connections.supabase] (pakai 's' di belakang connection)")
    st.stop()

# 3. FUNGSI HELPER
def get_kelas_list():
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))]
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))]
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))]
    return kx + kxi + kxii

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 class='main-header'>🏥 LOGIN UKS DIGITAL MAN 1</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("logo_uks.png"): 
            st.image("logo_uks.png", use_container_width=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("MASUK KE SISTEM"):
            if u == "adminuks" and p == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Username atau Password Salah!")
else:
    # 5. SIDEBAR NAVIGASI
    menu = st.sidebar.radio("NAVIGASI UTAMA:", 
    ["📊 Dashboard Utama", "📝 Input Pasien Harian", "💊 Stok Obat", "📅 Kegiatan Besar UKS", "📊 Pusat Laporan", "Keluar"])
    st.sidebar.markdown("<h2 style='text-align:center;'>🏥 UKS DIGITAL</h2>", unsafe_allow_html=True)
    if os.path.exists("logo_uks.png"):
        st.sidebar.image("logo_uks.png")
        
    if menu == "Keluar":
        st.session_state.auth = False
        st.rerun()

    # --- FITUR 1: INPUT PASIEN HARIAN ---
    if menu == "📝 Input Pasien Harian":
        st.markdown("<h2 style='color:#2e7d32;'>📝 Form Kunjungan Siswa</h2>", unsafe_allow_html=True)
        try:
            res_siswa = conn.table("master_siswa").select("*").execute()
            df_siswa = pd.DataFrame(res_siswa.data)
        except:
            df_siswa = pd.DataFrame(columns=['nama_siswa', 'kelas'])
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pilih_kls = st.selectbox("Pilih Kelas:", get_kelas_list())
        with col_p2:
            filtered_names = df_siswa[df_siswa['kelas'] == pilih_kls]['nama_siswa'].tolist()
            pilih_nama = st.selectbox("Pilih Nama Siswa:", sorted(filtered_names) if filtered_names else ["Data Siswa Kosong"])

        with st.form("form_kunjungan", clear_on_submit=True):
            keluhan = st.text_area("Keluhan / Diagnosa:")
            tindakan = st.text_input("Obat atau Tindakan:")
            petugas_piket = st.text_input("Nama Petugas Piket:")
            if st.form_submit_button("SIMPAN DATA KUNJUNGAN"):
                if keluhan and pilih_nama != "Data Siswa Kosong":
                    conn.table("data_pasien").insert({
                        "nama_siswa": pilih_nama,
                        "kelas": pilih_kls,
                        "keluhan": keluhan,
                        "obat_tindakan": tindakan,
                        "petugas": petugas_piket
                    }).execute()
                    st.success(f"✅ Data {pilih_nama} berhasil dicatat!")
                    st.balloons()
                else:
                    st.error("Mohon lengkapi data!")

    # --- FITUR 2: STOK OBAT ---
    elif menu == "💊 Stok Obat":
        st.markdown("<h2 style='color:#2e7d32;'>💊 Manajemen Stok Obat</h2>", unsafe_allow_html=True)
        with st.form("form_stok", clear_on_submit=True):
            c_o1, c_o2, c_o3 = st.columns([3,1,1])
            nama_o = c_o1.text_input("Nama Obat:")
            jumlah_o = c_o2.number_input("Jumlah:", min_value=0)
            satuan_o = c_o3.selectbox("Satuan:", ["Tablet", "Pcs", "Botol", "Sachet", "Strip"])
            if st.form_submit_button("UPDATE STOK"):
                if nama_o:
                    conn.table("stok_obat").upsert({"nama_obat": nama_o, "jumlah": jumlah_o, "satuan": satuan_o}).execute()
                    st.success(f"Stok {nama_o} diperbarui!")
                else:
                    st.error("Nama obat kosong.")

        st.subheader("📋 Daftar Inventaris Obat")
        try:
            res_stok = conn.table("stok_obat").select("*").execute()
            st.dataframe(pd.DataFrame(res_stok.data), use_container_width=True)
        except:
            st.info("Belum ada data stok obat.")

    # --- FITUR 3: KEGIATAN BESAR UKS (Donor Darah, dll) ---
    elif menu == "📅 Kegiatan Besar UKS":
        st.markdown("<h2 style='color:#2e7d32;'>📅 Laporan Kegiatan Khusus</h2>", unsafe_allow_html=True)
        with st.form("form_event", clear_on_submit=True):
            tgl_keg = st.date_input("Tanggal Pelaksanaan:")
            nama_keg = st.text_input("Nama Kegiatan:")
            lokasi_keg = st.text_input("Lokasi:")
            peserta_keg = st.number_input("Jumlah Peserta:", min_value=0)
            ket_keg = st.text_area("Keterangan / Hasil:")
            if st.form_submit_button("CATAT KEGIATAN"):
                if nama_keg:
                    data_event = {
                        "tanggal": str(tgl_keg),
                        "nama_kegiatan": nama_keg,
                        "lokasi": lokasi_keg,
                        "jumlah_peserta": peserta_keg,
                        "keterangan": ket_keg
                    }
                    conn.table("kegiatan_uks").insert(data_event).execute()
                    st.success("✅ Kegiatan berhasil dicatat!")
                else:
                    st.error("Nama kegiatan wajib diisi!")

    # --- FITUR 4: PUSAT LAPORAN ---
    elif menu == "📊 Pusat Laporan":
        st.markdown("<h2 style='color:#2e7d32;'>📊 Pusat Laporan Digital</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Riwayat Pasien", "Riwayat Kegiatan"])
        with t1:
            try:
                rp = conn.table("data_pasien").select("*").order("waktu", desc=True).execute()
                dfp = pd.DataFrame(rp.data)
                if not dfp.empty:
                    st.download_button("📥 Download CSV Pasien", dfp.to_csv(index=False), "pasien.csv")
                    st.dataframe(dfp, use_container_width=True)
                else:
                    st.info("Belum ada data pasien.")
            except:
                st.error("Gagal mengambil data pasien.")
        with t2:
            try:
                rk = conn.table("kegiatan_uks").select("*").order("tanggal", desc=True).execute()
                dfk = pd.DataFrame(rk.data)
                if not dfk.empty:
                    st.download_button("📥 Download CSV Kegiatan", dfk.to_csv(index=False), "kegiatan.csv")
                    st.dataframe(dfk, use_container_width=True)
                else:
                    st.info("Belum ada data kegiatan.")
            except:
                st.error("Gagal mengambil data kegiatan.")

st.markdown("---")
st.caption("© 2026 UKS Digital MAN 1 Kota Sukabumi")
