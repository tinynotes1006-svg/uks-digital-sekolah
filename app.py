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
    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #10b981;
        text-align: center;
    }
    .login-box {
        background: white; padding: 40px; border-radius: 24px; width: 400px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE
FILES = {
    "pasien": "data_pasien.csv", 
    "stok": "data_stok.csv", 
    "kegiatan": "data_kegiatan.csv", 
    "siswa": "db_siswa.csv"
}

def load_data(key):
    # Kolom default untuk setiap file jika file belum ada
    cols_map = {
        "pasien": ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"],
        "stok": ["Obat", "Stok", "Satuan"],
        "kegiatan": ["Tanggal", "Kegiatan", "Peserta", "Keterangan"],
        "siswa": ["nama_siswa", "kelas"]
    }
    cols = cols_map.get(key, [])
    
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
    return [f"{tk}-{chr(i)}" for tk in ["X", "XI", "XII"] for i in range(ord('A'), ord('K'))]

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("logo_uks.png", width=120) 
        st.markdown("<h2 style='color:#064e3b;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        user = st.text_input("Username", placeholder="adminuks")
        pw = st.text_input("Password", type="password")
        if st.button("Masuk", use_container_width=True):
            if user == "adminuks" and pw == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Akses Ditolak")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=80) 
        st.markdown("<h4 style='color:#064e3b;'>MAN 1 SUKABUMI</h4></div>---", unsafe_allow_html=True)
        menu = st.radio("Menu Utama:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])
        if st.button("🚪 Keluar Sistem"):
            st.session_state.auth = False
            st.rerun()

    # 6. DASHBOARD
    if menu == "📊 Dashboard":
        c_h1, c_h2 = st.columns([0.1, 0.9])
        with c_h1: st.image("logo_uks.png", width=60)
        with c_h2: st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
        
        df_p = load_data("pasien")
        df_o = load_data("stok")
        df_k = load_data("kegiatan")
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><h5>Kunjungan</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><h5>Kegiatan</h5><h2>{len(df_k)}</h2></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><h5>Jenis Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### 📈 Statistik Kunjungan")
        if not df_p.empty:
            df_p['Waktu'] = pd.to_datetime(df_p['Waktu'], errors='coerce')
            chart_data = df_p.dropna(subset=['Waktu']).groupby(df_p['Waktu'].dt.date).size()
            st.area_chart(chart_data, color="#10b981")

    # 7. INPUT PASIEN (REAKTIF)
    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>📝 Registrasi Pasien</h1>", unsafe_allow_html=True)
        df_s = load_data("siswa")
        df_p = load_data("pasien")

        with st.expander("➕ Tambah Master Data Siswa Baru"):
            with st.form("f_s", clear_on_submit=True):
                ns = st.text_input("Nama Lengkap")
                ks = st.selectbox("Kelas", get_list_kelas())
                if st.form_submit_button("Daftarkan Siswa"):
                    if ns:
                        df_s = pd.concat([df_s, pd.DataFrame([[ns, ks]], columns=df_s.columns)], ignore_index=True)
                        save_data(df_s, "siswa"); st.success("Siswa Terdaftar!"); st.rerun()

        st.subheader("Input Kunjungan")
        pilih_kls = st.selectbox("1. Pilih Kelas", get_list_kelas())
        names = sorted(df_s[df_s['kelas'] == pilih_kls]['nama_siswa'].unique().tolist())

        with st.form("f_p", clear_on_submit=True):
            if names:
                n_psn = st.selectbox("2. Pilih Nama Siswa", names, key=f"n_{pilih_kls}")
                kel = st.text_area("3. Keluhan")
                tin = st.text_input("4. Tindakan")
                if st.form_submit_button("➕ Simpan Kunjungan"):
                    wkt = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_p = pd.DataFrame([[wkt, n_psn, pilih_kls, kel, tin]], columns=df_p.columns)
                    save_data(pd.concat([df_p, new_p], ignore_index=True), "pasien")
                    st.success("Tersimpan!"); st.rerun()
            else:
                st.warning(f"Belum ada siswa di kelas {pilih_kls}")
                st.form_submit_button("Simpan", disabled=True)

    # 8. STOK OBAT
    elif menu == "💊 Stok Obat":
        st.markdown("<h1 class='main-header'>💊 Stok Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok")
        with st.form("f_o", clear_on_submit=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1: on = st.text_input("Nama Obat")
            with c2: js = st.number_input("Jumlah", min_value=0)
            with c3: us = st.selectbox("Satuan", ["Tablet", "Strip", "Pcs", "Botol", "Tube", "Sachet", "Kapsul", "Kaplet", "Pot", "Box", "Blister", "mL", "Unit"])
            if st.form_submit_button("➕ Simpan Stok"):
                if on:
                    df_o = pd.concat([df_o, pd.DataFrame([[on, js, us]], columns=df_o.columns)], ignore_index=True)
                    save_data(df_o, "stok"); st.success("Stok Terupdate!"); st.rerun()
        st.dataframe(df_o, use_container_width=True)

    # 9. KEGIATAN
    elif menu == "📅 Kegiatan":
        st.markdown("<h1 class='main-header'>📅 Laporan Kegiatan</h1>", unsafe_allow_html=True)
        df_k = load_data("kegiatan")
        with st.form("f_k", clear_on_submit=True):
            tgl = st.date_input("Tanggal")
            keg = st.text_input("Nama Kegiatan")
            pes = st.number_input("Peserta", min_value=0)
            ket = st.text_area("Keterangan")
            if st.form_submit_button("➕ Simpan Kegiatan"):
                if keg:
                    df_k = pd.concat([df_k, pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df_k.columns)], ignore_index=True)
                    save_data(df_k, "kegiatan"); st.success("Kegiatan Dicatat!"); st.rerun()
        st.dataframe(df_k, use_container_width=True)

    # 10. KELOLA DATA (BISA UNDUH SEMUA)
    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>📥 Kelola & Unduh Data</h1>", unsafe_allow_html=True)
        st.info("Di sini Anda dapat mengunduh semua database UKS atau menghapus data yang salah.")
        
        # Grid layout untuk kartu download
        tabs = st.tabs(["🏥 Data Pasien", "💊 Data Stok", "📅 Data Kegiatan", "👥 Data Siswa"])
        
        with tabs[0]:
            d_pasien = load_data("pasien")
            st.download_button("📥 Download Data Pasien (.csv)", d_pasien.to_csv(index=False), "data_pasien.csv", "text/csv")
            if st.button("🗑️ Hapus Baris Terakhir Pasien"):
                save_data(d_pasien[:-1], "pasien"); st.rerun()
            st.dataframe(d_pasien, use_container_width=True)

        with tabs[1]:
            d_stok = load_data("stok")
            st.download_button("📥 Download Data Stok (.csv)", d_stok.to_csv(index=False), "data_stok.csv", "text/csv")
            if st.button("🗑️ Hapus Baris Terakhir Stok"):
                save_data(d_stok[:-1], "stok"); st.rerun()
            st.dataframe(d_stok, use_container_width=True)

        with tabs[2]:
            d_keg = load_data("kegiatan")
            st.download_button("📥 Download Data Kegiatan (.csv)", d_keg.to_csv(index=False), "data_kegiatan.csv", "text/csv")
            if st.button("🗑️ Hapus Baris Terakhir Kegiatan"):
                save_data(d_keg[:-1], "kegiatan"); st.rerun()
            st.dataframe(d_keg, use_container_width=True)

        with tabs[3]:
            d_siswa = load_data("siswa")
            st.download_button("📥 Download Database Siswa (.csv)", d_siswa.to_csv(index=False), "db_siswa.csv", "text/csv")
            if st.button("🗑️ Hapus Baris Terakhir Siswa"):
                save_data(d_siswa[:-1], "siswa"); st.rerun()
            st.dataframe(d_siswa, use_container_width=True)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | UKS Digital System")
