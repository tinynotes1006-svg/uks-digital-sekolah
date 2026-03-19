import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS UNTUK TAMPILAN RAPI & SIMETRIS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #10b981;
        text-align: center;
    }
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.3rem; margin: 0;
    }
    .login-box {
        background: white; padding: 40px; border-radius: 24px; width: 400px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE CSV (Mencegah KeyError & ValueError)
FILES = {
    "pasien": "data_pasien.csv", 
    "stok": "data_stok.csv", 
    "kegiatan": "data_kegiatan.csv", 
    "siswa": "db_siswa.csv"
}

def load_data(key, cols):
    if os.path.exists(FILES[key]):
        try:
            df = pd.read_csv(FILES[key])
            # Pastikan kolom sesuai, jika tidak buat ulang
            if list(df.columns) != cols:
                return pd.DataFrame(columns=cols)
            return df
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        # Logo UKS di Tengah Halaman Login
        st.image("logo_uks.png", width=120) 
        st.markdown("<h2 style='color:#064e3b; margin-top:10px;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="adminuks", label_visibility="collapsed")
        pw = st.text_input("Password", type="password", placeholder="man1sukabumi", label_visibility="collapsed")
        if st.button("Masuk ke Sistem", use_container_width=True):
            if user == "adminuks" and pw == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Login Gagal")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR (LOGO SEKOLAH)
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=80) 
        st.markdown("<h4 style='color:#064e3b;'>MAN 1 SUKABUMI</h4></div>---", unsafe_allow_html=True)
        menu = st.radio("Pilih Menu:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])
        st.markdown("---")
        if st.button("🚪 Keluar"):
            st.session_state.auth = False
            st.rerun()

    # 6. MENU DASHBOARD
    if menu == "📊 Dashboard":
        col_h1, col_h2 = st.columns([0.1, 0.9])
        with col_h1: st.image("logo_uks.png", width=60)
        with col_h2: st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
        
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        df_k = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
        
        # Metrik Utama
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><h5>Total Pasien</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><h5>Total Kegiatan</h5><h2>{len(df_k)}</h2></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><h5>Jenis Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        
        # Statistik Kunjungan
        st.markdown("### 📈 Statistik Kunjungan Siswa")
        if not df_p.empty:
            # Proteksi error kolom Waktu
            df_p['Waktu'] = pd.to_datetime(df_p['Waktu'], errors='coerce')
            df_p = df_p.dropna(subset=['Waktu'])
            if not df_p.empty:
                chart_data = df_p.groupby(df_p['Waktu'].dt.date).size()
                st.area_chart(chart_data, color="#10b981")
        else: st.info("Belum ada data kunjungan.")

    # 7. MENU STOK OBAT (DENGAN ICON TAMBAH & SATUAN LENGKAP)
    elif menu == "💊 Stok Obat":
        st.markdown("<h1 class='main-header'>💊 Inventaris Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        
        with st.expander("➕ Tambah Data Obat Baru", expanded=True):
            with st.form("form_stok", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: n_obat = st.text_input("Nama Obat")
                with c2: j_obat = st.number_input("Jumlah", min_value=0)
                with c3: s_obat = st.selectbox("Satuan", ["Tablet", "Strip", "Pcs", "Botol", "Tube", "Sachet", "Kapsul", "Kaplet", "Pot", "Box", "Blister", "mL", "Unit"])
                
                if st.form_submit_button("➕ Simpan Obat"):
                    if n_obat:
                        df_o = pd.concat([df_o, pd.DataFrame([[n_obat, j_obat, s_obat]], columns=df_o.columns)], ignore_index=True)
                        save_data(df_o, "stok")
                        st.success("Data Tersimpan!"); st.rerun()
        
        st.dataframe(df_o, use_container_width=True)

    # 8. MENU KEGIATAN (FIX VALUE ERROR)
    elif menu == "📅 Kegiatan":
        st.markdown("<h1 class='main-header'>📅 Laporan Kegiatan</h1>", unsafe_allow_html=True)
        df_k = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
        with st.form("form_keg"):
            tgl = st.date_input("Tanggal")
            keg = st.text_input("Nama Acara/Kegiatan")
            pes = st.number_input("Jumlah Peserta", min_value=0)
            ket = st.text_area("Keterangan")
            if st.form_submit_button("➕ Simpan Kegiatan"):
                if keg:
                    # Fix ValueError: Pastikan jumlah kolom sama
                    new_data = pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df_k.columns)
                    df_k = pd.concat([df_k, new_data], ignore_index=True)
                    save_data(df_k, "kegiatan")
                    st.success("Kegiatan Dicatat!"); st.rerun()
        st.dataframe(df_k, use_container_width=True)

   # FORM 2: INPUT KUNJUNGAN (Filter Dinamis)
    st.subheader("Catat Kunjungan Baru")
    with st.form("f_kunjungan", clear_on_submit=True):
        # 1. Pilih Kelas terlebih dahulu
        pilih_kelas = st.selectbox("1. Pilih Kelas", get_list_kelas())
        
        # 2. Filter nama siswa berdasarkan kelas yang dipilih
        if not df_s.empty:
            daftar_nama = df_s[df_s['kelas'] == pilih_kelas]['nama_siswa'].unique().tolist()
        else:
            daftar_nama = []
        
        # 3. Tampilkan pilihan nama (atau pesan jika kosong)
        if daftar_nama:
            nama_pasien = st.selectbox("2. Pilih Nama Siswa", sorted(daftar_nama))
            keluhan = st.text_area("3. Keluhan / Sakit")
            tindakan = st.text_input("4. Tindakan (Contoh: Istirahat / Kasih Obat)")
            
            submit_pasien = st.form_submit_button("➕ Simpan Kunjungan")
            
            if submit_pasien:
                if keluhan:
                    waktu_skrg = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_entry = pd.DataFrame([[waktu_skrg, nama_pasien, pilih_kelas, keluhan, tindakan]], columns=df_p.columns)
                    df_p = pd.concat([df_p, new_entry], ignore_index=True)
                    save_data(df_p, "pasien")
                    st.success(f"Data kunjungan {nama_pasien} berhasil disimpan!")
                    st.balloons()
        else:
            st.warning(f"Belum ada data siswa untuk kelas {pilih_kelas}. Silakan tambah siswa di menu atas.")
            st.form_submit_button("Simpan Kunjungan", disabled=True)

    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>📥 Hapus & Ekspor Data</h1>", unsafe_allow_html=True)
        for k in ["pasien", "stok", "kegiatan"]:
            d = load_data(k, ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"] if k=="pasien" else [])
            if not d.empty:
                st.write(f"Data {k.capitalize()}")
                if st.button(f"🗑️ Hapus Baris Terakhir {k}"):
                    save_data(d[:-1], k); st.rerun()
                st.dataframe(d)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | Terintegrasi Dashboard UKS")
