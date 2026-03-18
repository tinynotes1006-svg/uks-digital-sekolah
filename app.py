import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime
import os

# 1. KONFIGURASI HALAMAN & STYLE CSS (HIJAU MAN 1 LEBIH TERANG)
st.set_page_config(page_title="UKS Digital MAN 1 Kota Sukabumi", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    /* Mengubah warna font navigasi sidebar */
    [data-testid="stSidebar"] {
        background-color: #004d40; /* Hijau Tua untuk Sidebar agar Kontras */
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Mengubah warna tombol (Primary Button) - Hijau Lebih Terang */
    .stButton>button {
        background-color: #00c853; /* Hijau Terang Menyala */
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #00e676; /* Hijau Lebih Terang saat Hover */
        color: white;
        border: 1px solid #a5d6a7;
    }

    /* Header Styling */
    .main-header {
        text-align: center; 
        color: #1b5e20; /* Hijau Tua untuk Tulisan */
        padding: 10px;
        border-bottom: 3px solid #00c853;
        margin-bottom: 20px;
    }

    /* Card Styling untuk Form - Hijau Wash Terang */
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background-color: #e8f5e9; /* Hijau Sangat Muda Terang */
    }
    
    /* Login Page Logo Styling - Perkecil Ukuran */
    .login-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 150px; /* Ukuran Logo UKS di Login Diperkecil */
        margin-bottom: 20px;
    }
    
    /* Sekolah Name Styling di Login */
    .sekolah-name-login {
        text-align: center;
        color: #1b5e20;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sekolah-sub-login {
        text-align: center;
        color: #43a047;
        font-size: 18px;
        margin-bottom: 25px;
    }

    /* Input Styling */
    input, textarea {
        border-radius: 5px !important;
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

# 3. FUNGSI HELPER
def get_kelas_list():
    # Filter Kelas Sesuai Permintaan
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))] # A-J
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))] # A-K
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))] # A-J
    return kx + kxi + kxii

# 4. SISTEM LOGIN (ANTI-LOGOUT SESSION)
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # HALAMAN LOGIN DENGAN LOGO KECIL DAN NAMA SEKOLAH
    st.markdown("<div class='sekolah-name-login'>MAN 1 Kota Sukabumi</div>", unsafe_allow_html=True)
    st.markdown("<div class='sekolah-sub-login'>🏥 SISTEM UKS DIGITAL</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("logo_uks.png"): 
            # Menampilkan logo UKS diperkecil menggunakan HTML & CSS class
            st.markdown(f'<img src="data:image/png;base64,{st.image("logo_uks.png", output_format="PNG").base64}" class="login-logo">', unsafe_allow_html=True)
        
        with st.container():
            u = st.text_input("Username", placeholder="adminuks")
            p = st.text_input("Password", type="password", placeholder="man1sukabumi")
            if st.button("MASUK KE SISTEM"):
                if u == "adminuks" and p == "man1sukabumi":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Username atau Password Salah!")
else:
    # 5. SIDEBAR NAVIGASI DENGAN LOGO SEKOLAH & NAMA
    st.sidebar.markdown(f"<h3 style='text-align:center;'>🏥 UKS DIGITAL</h3>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:#a5d6a7;'>MAN 1 Kota Sukabumi</p>", unsafe_allow_html=True)
    
    if os.path.exists("logo_sekolah.png"):
        st.sidebar.image("logo_sekolah.png", use_container_width=True)
    
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("NAVIGASI UTAMA:", 
        ["📊 Dashboard Utama", "📝 Input Pasien Harian", "💊 Stok Obat", "📅 Kegiatan Besar UKS", "📊 Pusat Laporan", "Keluar"])
    
    if menu == "Keluar":
        st.session_state.auth = False
        st.rerun()

    # Ambil Data dari Supabase untuk Halaman Menu
    try:
        res_p = conn.table("data_pasien").select("*").execute()
        res_o = conn.table("stok_obat").select("*").execute()
        res_k = conn.table("kegiatan_uks").select("*").execute()
        
        df_p = pd.DataFrame(res_p.data)
        df_o = pd.DataFrame(res_o.data)
        df_k = pd.DataFrame(res_k.data)
    except:
        df_p = pd.DataFrame()
        df_o = pd.DataFrame()
        df_k = pd.DataFrame()

    # --- FITUR A: DASHBOARD UTAMA ---
    if menu == "📊 Dashboard Utama":
        st.markdown("<h2 class='main-header'>📊 DASHBOARD STATISTIK UKS</h2>", unsafe_allow_html=True)
        
        # --- BARIS 1: RINGKASAN ANGKA ---
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div style='background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #00c853;'>
                    <h4 style='color: #1b5e20; margin:0;'>Total Pasien</h4>
                    <h2 style='margin:0; color: #00c853;'>{}</h2>
                    <p style='color:grey; font-size:12px; margin:0;'>Siswa yang pernah berkunjung</p>
                </div>
            """.format(len(df_p)), unsafe_allow_html=True)
            
        with col2:
            st.markdown("""
                <div style='background-color: #fff3e0; padding: 20px; border-radius: 10px; border-left: 5px solid #ff9800;'>
                    <h4 style='color: #ef6c00; margin:0;'>Jenis Obat</h4>
                    <h2 style='margin:0; color: #ff9800;'>{}</h2>
                    <p style='color:grey; font-size:12px; margin:0;'>Varian obat di inventaris</p>
                </div>
            """.format(len(df_o)), unsafe_allow_html=True)

        with col3:
            st.markdown("""
                <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #2196f3;'>
                    <h4 style='color: #1565c0; margin:0;'>Total Kegiatan</h4>
                    <h2 style='margin:0; color: #2196f3;'>{}</h2>
                    <p style='color:grey; font-size:12px; margin:0;'>Event besar yang terlaksana</p>
                </div>
            """.format(len(df_k)), unsafe_allow_html=True)

        st.markdown("---")

        # --- BARIS 2: ANALISIS DETAIL ---
        c_left, c_right = st.columns(2)
        
        with c_left:
            st.subheader("⚠️ Stok Obat Hampir Habis (<= 10)")
            if not df_o.empty:
                # Filter obat yang jumlahnya di bawah 10
                obat_kritis = df_o[df_o['jumlah'] <= 10]
                if not obat_kritis.empty:
                    st.warning(f"Ada {len(obat_kritis)} obat yang harus segera dipesan!")
                    st.table(obat_kritis[['nama_obat', 'jumlah', 'satuan']])
                else:
                    st.success("✅ Semua stok obat masih aman.")
            else:
                st.info("Belum ada data stok obat.")

        with c_right:
            st.subheader("🕒 5 Kunjungan Pasien Terakhir")
            if not df_p.empty:
                # Ambil 5 data terbaru, urutkan berdasarkan waktu
                recent_p = df_p.sort_values(by='waktu', ascending=False).head(5)
                # Rapikan format waktu agar mudah dibaca
                recent_p['waktu'] = pd.to_datetime(recent_p['waktu']).dt.strftime('%d %B %Y, %H:%M')
                st.write(recent_p[['waktu', 'nama_siswa', 'keluhan', 'obat_tindakan']])
            else:
                st.info("Belum ada data kunjungan pasien.")

    # --- FITUR 1: INPUT PASIEN HARIAN ---
    elif menu == "📝 Input Pasien Harian":
        st.markdown("<h2 style='color:#1b5e20;'>📝 Form Kunjungan Siswa Harian</h2>", unsafe_allow_html=True)
        
        # Ambil data master siswa dari Supabase
        try:
            res_siswa = conn.table("master_siswa").select("*").execute()
            df_siswa = pd.DataFrame(res_siswa.data)
        except:
            df_siswa = pd.DataFrame(columns=['nama_siswa', 'kelas'])
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pilih_kls = st.selectbox("Pilih Kelas Siswa:", get_kelas_list())
        with col_p2:
            # Filter nama siswa berdasarkan kelas yang dipilih
            filtered_names = df_siswa[df_siswa['kelas'] == pilih_kls]['nama_siswa'].tolist()
            pilih_nama = st.selectbox("Pilih Nama Siswa:", sorted(filtered_names) if filtered_names else ["Data Siswa Kosong"])

        # Form Input Pasien
        with st.form("form_kunjungan", clear_on_submit=True):
            keluhan = st.text_area("Keluhan / Diagnosa Utama:")
            tindakan = st.text_input("Obat atau Tindakan yang diberikan:", placeholder="Misal: Paracetamol 1 tab, Istirahat 30 mnt")
            petugas_piket = st.text_input("Nama Petugas Piket (Guru/PMR):")
            
            if st.form_submit_button("SIMPAN DATA KUNJUNGAN"):
                if keluhan and pilih_nama != "Data Siswa Kosong":
                    data_input = {
                        "nama_siswa": pilih_nama,
                        "kelas": pilih_kls,
                        "keluhan": keluhan,
                        "obat_tindakan": tindakan,
                        "petugas": petugas_piket
                    }
                    try:
                        conn.table("data_pasien").insert(data_input).execute()
                        st.success(f"✅ Data kunjungan {pilih_nama} berhasil dicatat!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")
                else:
                    st.error("Mohon lengkapi data keluhan dan pastikan nama siswa terpilih!")

    # --- FITUR 2: STOK OBAT ---
    elif menu == "💊 Stok Obat":
        st.markdown("<h2 style='color:#1b5e20;'>💊 Manajemen Inventaris Stok Obat</h2>", unsafe_allow_html=True)
        
        # Form Update Stok Obat (Upsert)
        with st.form("form_stok", clear_on_submit=True):
            st.subheader("➕ Update / Tambah Stok Obat")
            c_o1, c_o2, c_o3 = st.columns([3,1,1])
            nama_o = c_o1.text_input("Nama Lengkap Obat:")
            jumlah_o = c_o2.number_input("Jumlah Stok:", min_value=0, step=1)
            satuan_o = c_o3.selectbox("Satuan:", ["Tablet", "Pcs", "Botol", "Sachet", "Strip", "Salep"])
            
            if st.form_submit_button("UPDATE STOK"):
                if nama_o:
                    try:
                        conn.table("stok_obat").upsert({"nama_obat": nama_o, "jumlah": jumlah_o, "satuan": satuan_o}).execute()
                        st.success(f"✅ Stok {nama_o} berhasil diperbarui menjadi {jumlah_o} {satuan_o}!")
                    except Exception as e:
                        st.error(f"Gagal memperbarui stok: {e}")
                else:
                    st.error("Nama obat tidak boleh kosong.")

        st.markdown("---")
        st.subheader("📋 Daftar Seluruh Inventaris Obat")
        if not df_o.empty:
            st.dataframe(df_o, use_container_width=True)
        else:
            st.info("Belum ada data inventaris obat.")

    # --- FITUR 3: KEGIATAN BESAR UKS (Donor Darah, Imunisasi, dll) ---
    elif menu == "📅 Kegiatan Besar UKS":
        st.markdown("<h2 style='color:#1b5e20;'>📅 Laporan Kegiatan Khusus (Event) UKS</h2>", unsafe_allow_html=True)
        
        # Form Input Kegiatan Besar
        with st.form("form_event", clear_on_submit=True):
            st.subheader("➕ Catat Kegiatan Baru")
            tgl_keg = st.date_input("Tanggal Pelaksanaan Kegiatan:")
            nama_keg = st.text_input("Nama Kegiatan:", placeholder="Contoh: Donor Darah PMI, Imunisasi BIAS, Pemeriksaan Gigi")
            lokasi_keg = st.text_input("Lokasi Pelaksanaan:", placeholder="Misal: Aula MAN 1, Ruang UKS")
            peserta_keg = st.number_input("Jumlah Peserta / Siswa:", min_value=0, step=1)
            ket_keg = st.text_area("Keterangan / Hasil / Detail Kegiatan:")
            
            if st.form_submit_button("CATAT KEGIATAN"):
                if nama_keg:
                    data_event = {
                        "tanggal": str(tgl_keg),
                        "nama_kegiatan": nama_keg,
                        "lokasi": lokasi_keg,
                        "jumlah_peserta": peserta_keg,
                        "keterangan": ket_keg
                    }
                    try:
                        conn.table("kegiatan_uks").insert(data_event).execute()
                        st.success("✅ Kegiatan besar berhasil dicatat ke database!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Gagal mencatat kegiatan: {e}")
                else:
                    st.error("Nama kegiatan wajib diisi!")

    # --- FITUR 4: PUSAT LAPORAN ---
    elif menu == "📊 Pusat Laporan":
        st.markdown("<h2 style='color:#1b5e20;'>📊 Pusat Unduh Laporan Digital</h2>", unsafe_allow_html=True)
        st.info("Gunakan tab di bawah untuk melihat dan mengunduh laporan dalam format Excel/CSV.")
        
        tab_harian, tab_kegiatan = st.tabs(["📋 Riwayat Pasien Harian", "📅 Riwayat Kegiatan Besar"])
        
        with tab_harian:
            try:
                # Ambil data pasien terbaru urut dari waktu terbaru
                res_lap_p = conn.table("data_pasien").select("*").order("waktu", desc=True).execute()
                df_lap_p = pd.DataFrame(res_lap_p.data)
                
                if not df_lap_p.empty:
                    st.download_button("📥 Download Excel Pasien (CSV)", df_lap_p.to_csv(index=False), "laporan_pasien_harian_man1.csv", "text/csv", use_container_width=True)
                    st.dataframe(df_lap_p, use_container_width=True)
                else:
                    st.info("Belum ada data riwayat pasien.")
            except:
                st.error("Gagal mengambil data laporan pasien.")
                
        with tab_kegiatan:
            try:
                # Ambil data kegiatan terbaru urut dari tanggal terbaru
                res_lap_k = conn.table("kegiatan_uks").select("*").order("tanggal", desc=True).execute()
                df_lap_k = pd.DataFrame(res_lap_k.data)
                
                if not df_lap_k.empty:
                    st.download_button("📥 Download Excel Kegiatan (CSV)", df_lap_k.to_csv(index=False), "laporan_kegiatan_besar_man1.csv", "text/csv", use_container_width=True)
                    st.dataframe(df_lap_k, use_container_width=True)
                else:
                    st.info("Belum ada data riwayat kegiatan besar.")
            except:
                st.error("Gagal mengambil data laporan kegiatan.")

# FOOTER KONSISTEN
st.markdown("---")
st.markdown("<p style='text-align: center; color: grey;'>© 2026 UKS Digital MAN 1 Kota Sukabumi | Powered by Streamlit & Supabase</p>", unsafe_allow_html=True)
