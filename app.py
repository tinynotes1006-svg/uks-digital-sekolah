import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN & STYLE CSS
st.set_page_config(page_title="UKS Digital MAN 1 Kota Sukabumi", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    /* Container Logo 50px Sejajar */
    .logo-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        gap: 15px; 
        margin-bottom: 5px; 
    }
    .login-logo-img { 
        width: 50px; 
        height: 50px; 
        object-fit: contain; 
    }
    /* Warna Hijau MAN 1 */
    [data-testid="stSidebar"] { background-color: #004d40; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton>button { 
        background-color: #00c853; 
        color: white; 
        border-radius: 8px; 
        font-weight: bold; 
        width: 100%; 
        border: none; 
        height: 3em; 
    }
    .stButton>button:hover { background-color: #00e676; }
    .sekolah-name-login { text-align: center; color: #1b5e20; font-size: 20px; font-weight: bold; margin-top: 5px; }
    .sekolah-sub-login { text-align: center; color: #43a047; font-size: 14px; margin-bottom: 20px; }
    .main-header { text-align: center; color: #1b5e20; border-bottom: 2px solid #00c853; padding: 10px; margin-bottom: 20px; }
    .stForm { background-color: #f1f8e9; border-radius: 10px; padding: 20px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEM DATABASE CSV LOKAL
FILES = {
    "pasien": "data_pasien.csv",
    "stok": "data_stok.csv",
    "kegiatan": "data_kegiatan.csv",
    "siswa": "db_siswa.csv"
}

def load_data(key, cols):
    if os.path.exists(FILES[key]):
        return pd.read_csv(FILES[key])
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

# 3. HELPER FILTER KELAS (MAN 1 SUKABUMI)
def list_kelas():
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))] # A-J
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))] # A-K
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))] # A-J
    return kx + kxi + kxii

# 4. SISTEM LOGIN & SESSION
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("###")
        # Menampilkan Logo Sekolah & UKS (Pastikan file ada di GitHub)
        st.markdown(f"""
            <div class="logo-container">
                <img src="https://raw.githubusercontent.com/{st.context.user}/uks-digital-sekolah/main/logo_sekolah.png" class="login-logo-img">
                <img src="https://raw.githubusercontent.com/{st.context.user}/uks-digital-sekolah/main/logo_uks.png" class="login-logo-img">
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='sekolah-name-login'>MAN 1 Kota Sukabumi</div>", unsafe_allow_html=True)
        st.markdown("<div class='sekolah-sub-login'>🏥 SISTEM MANAJEMEN UKS DIGITAL</div>", unsafe_allow_html=True)
        
        u = st.text_input("Username", placeholder="adminuks")
        p = st.text_input("Password", type="password", placeholder="man1sukabumi")
        if st.button("MASUK KE SISTEM"):
            if u == "adminuks" and p == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Login Gagal! Periksa kembali Username/Password.")
else:
    # 5. SIDEBAR NAVIGASI
    st.sidebar.markdown("<h3 style='text-align:center;'>🏥 MENU UTAMA</h3>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Pilih Menu:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan Besar", "📥 Ekspor Data", "Keluar"])
    
    if menu == "Keluar":
        st.session_state.auth = False
        st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 class='main-header'>📊 RINGKASAN DATA UKS</h2>", unsafe_allow_html=True)
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Kunjungan", len(df_p))
        c2.metric("Varian Obat", len(df_o))
        c3.metric("Status Sistem", "Berjalan Baik ✅")
        
        st.markdown("---")
        col_stok, col_pasien = st.columns(2)
        with col_stok:
            st.subheader("⚠️ Peringatan Stok Obat (<= 10)")
            if not df_o.empty:
                kritis = df_o[df_o['Stok'].astype(int) <= 10]
                if not kritis.empty: st.warning("Stok obat menipis!"); st.table(kritis)
                else: st.success("Semua stok aman.")
        with col_pasien:
            st.subheader("🕒 Kunjungan Terakhir")
            if not df_p.empty:
                st.write(df_p.sort_values(by='Waktu', ascending=False).head(5))

    # --- INPUT PASIEN & MANAJEMEN SISWA ---
    elif menu == "📝 Input Pasien":
        st.markdown("<h2 class='main-header'>📝 CATAT KUNJUNGAN SISWA</h2>", unsafe_allow_html=True)
        df_siswa = load_data("siswa", ["nama_siswa", "kelas"])
        
        # Sub-Menu Tambah Siswa
        with st.expander("➕ Tambah Nama Siswa Baru (Manajemen Siswa)"):
            with st.form("tambah_siswa", clear_on_submit=True):
                n_baru = st.text_input("Nama Lengkap Siswa Baru")
                k_baru = st.selectbox("Kelas Baru", list_kelas(), key="k_br")
                if st.form_submit_button("Simpan ke Database Siswa"):
                    if n_baru:
                        new_s = pd.DataFrame([[n_baru, k_baru]], columns=["nama_siswa", "kelas"])
                        df_siswa = pd.concat([df_siswa, new_s], ignore_index=True)
                        save_data(df_siswa, "siswa")
                        st.success(f"Siswa {n_baru} Berhasil Ditambahkan!")
                        st.rerun()

        st.write("---")
        # Form Kunjungan Harian
        with st.form("form_p", clear_on_submit=True):
            f_kelas = st.selectbox("Pilih Kelas Siswa", list_kelas())
            # Filter nama siswa otomatis berdasarkan kelas
            list_nama = df_siswa[df_siswa['kelas'] == f_kelas]['nama_siswa'].tolist()
            f_nama = st.selectbox("Pilih Nama Siswa", sorted(list_nama) if list_nama else ["Nama tidak ditemukan, tambah siswa di atas dulu"])
            
            f_keluhan = st.text_area("Keluhan / Diagnosa")
            f_tindakan = st.text_input("Obat / Tindakan yang diberikan")
            
            if st.form_submit_button("SIMPAN KUNJUNGAN"):
                if f_nama != "Nama tidak ditemukan, tambah siswa di atas dulu" and f_keluhan:
                    df = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
                    new_p = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), f_nama, f_kelas, f_keluhan, f_tindakan]], 
                                         columns=["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
                    df = pd.concat([df, new_p], ignore_index=True)
                    save_data(df, "pasien")
                    st.success("Data Berhasil Disimpan!"); st.balloons()
                else: st.error("Lengkapi data keluhan!")

    # --- STOK OBAT ---
    elif menu == "💊 Stok Obat":
        st.markdown("<h2 class='main-header'>💊 MANAJEMEN INVENTARIS OBAT</h2>", unsafe_allow_html=True)
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        with st.form("form_o", clear_on_submit=True):
            n_o = st.text_input("Nama Obat")
            j_o = st.number_input("Jumlah Stok", min_value=0)
            s_o = st.selectbox("Satuan", ["Tablet", "Botol", "Sachet", "Strip", "Pcs", "Salep"])
            if st.form_submit_button("UPDATE STOK"):
                if n_o:
                    if n_o in df_o['Obat'].values:
                        df_o.loc[df_o['Obat'] == n_o, ['Stok', 'Satuan']] = [j_o, s_o]
                    else:
                        df_o = pd.concat([df_o, pd.DataFrame([[n_o, j_o, s_o]], columns=["Obat", "Stok", "Satuan"])], ignore_index=True)
                    save_data(df_o, "stok")
                    st.success(f"Stok {n_o} diperbarui!")
                else: st.error("Isi Nama Obat!")
        st.dataframe(df_o, use_container_width=True)

    # --- KEGIATAN BESAR ---
    elif menu == "📅 Kegiatan Besar":
        st.markdown("<h2 class='main-header'>📅 LAPORAN KEGIATAN KHUSUS UKS</h2>", unsafe_allow_html=True)
        with st.form("form_k", clear_on_submit=True):
            tgl = st.date_input("Tanggal Pelaksanaan")
            keg = st.text_input("Nama Kegiatan (Contoh: Donor Darah, BIAS, Penjaringan)")
            pes = st.number_input("Jumlah Peserta", min_value=0)
            ket = st.text_area("Keterangan/Hasil Kegiatan")
            if st.form_submit_button("SIMPAN KEGIATAN"):
                if keg:
                    df = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
                    df = pd.concat([df, pd.DataFrame([[str(tgl), keg, pes, ket]], columns=["Tanggal", "Kegiatan", "Peserta", "Keterangan"])], ignore_index=True)
                    save_data(df, "kegiatan")
                    st.success("Kegiatan berhasil dicatat!")
                else: st.error("Nama kegiatan wajib diisi!")

    # --- EKSPOR DATA ---
    elif menu == "📥 Ekspor Data":
        st.markdown("<h2 class='main-header'>📥 PUSAT DOWNLOAD LAPORAN</h2>", unsafe_allow_html=True)
        st.info("💡 Karena sistem ini menggunakan penyimpanan internal, sangat disarankan untuk mendownload backup data setiap minggu.")
        
        t1, t2, t3, t4 = st.tabs(["Laporan Pasien", "Data Stok", "Data Kegiatan", "Data Siswa"])
        
        with t1:
            df = load_data("pasien", [])
            if not df.empty:
                st.download_button("📥 Unduh CSV Pasien", df.to_csv(index=False), "laporan_pasien.csv", "text/csv")
                st.dataframe(df)
        with t2:
            df = load_data("stok", [])
            if not df.empty:
                st.download_button("📥 Unduh CSV Stok", df.to_csv(index=False), "laporan_stok.csv", "text/csv")
                st.dataframe(df)
        with t3:
            df = load_data("kegiatan", [])
            if not df.empty:
                st.download_button("📥 Unduh CSV Kegiatan", df.to_csv(index=False), "laporan_kegiatan.csv", "text/csv")
                st.dataframe(df)
        with t4:
            df = load_data("siswa", [])
            if not df.empty:
                st.download_button("📥 Unduh Master Siswa", df.to_csv(index=False), "master_siswa.csv", "text/csv")
                st.dataframe(df)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | Sistem UKS Digital v2.0")
