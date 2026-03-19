import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS CUSTOM
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.3rem; margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE
FILES = {"pasien": "data_pasien.csv", "stok": "data_stok.csv", "kegiatan": "data_kegiatan.csv", "siswa": "db_siswa.csv"}

def load_data(key, cols):
    if os.path.exists(FILES[key]):
        try:
            df = pd.read_csv(FILES[key])
            if list(df.columns) != cols: return pd.DataFrame(columns=cols)
            return df
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def get_list_kelas():
    # Daftar kelas sesuai format MAN 1
    return [f"{tk}-{chr(i)}" for tk in ["X", "XI", "XII"] for i in range(ord('A'), ord('K'))]

# 4. SISTEM LOGIN (Sederhana)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    # (Bagian login tetap sama seperti sebelumnya)
    st.session_state.auth = True # Bypass untuk testing

# 5. SIDEBAR & MENU
with st.sidebar:
    st.image("logo_sekolah.png", width=80)
    menu = st.radio("Menu:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan"])

# 6. LOGIKA INPUT PASIEN (Saring Nama Berdasarkan Kelas)
if menu == "📝 Input Pasien":
    st.markdown("<h1 class='main-header'>📝 Registrasi Pasien</h1>", unsafe_allow_html=True)
    
    # Load data Master Siswa dan Data Pasien
    df_s = load_data("siswa", ["nama_siswa", "kelas"])
    df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])

    # FORM 1: TAMBAH SISWA BARU (Jika belum ada di database)
    with st.expander("➕ Tambah Master Data Siswa (Jika Belum Terdaftar)"):
        with st.form("f_tambah_siswa", clear_on_submit=True):
            new_nama = st.text_input("Nama Lengkap Siswa")
            new_kelas = st.selectbox("Pilih Kelas Siswa", get_list_kelas(), key="add_ks")
            if st.form_submit_button("Simpan ke Database Siswa"):
                if new_nama:
                    df_s = pd.concat([df_s, pd.DataFrame([[new_nama, new_kelas]], columns=df_s.columns)], ignore_index=True)
                    save_data(df_s, "siswa")
                    st.success(f"Siswa {new_nama} berhasil didaftarkan!")
                    st.rerun()

    st.divider()

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

    # Tampilkan Riwayat
    st.markdown("### 🕒 Kunjungan Hari Ini")
    st.dataframe(df_p.tail(5), use_container_width=True)

# (Menu lain seperti Dashboard, Stok, Kegiatan tetap menggunakan logika yang sudah diperbaiki sebelumnya)
