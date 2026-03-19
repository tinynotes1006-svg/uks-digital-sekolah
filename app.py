import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS UNTUK TAMPILAN MODERN & RAPI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Login Box */
    .login-container { display: flex; justify-content: center; align-items: center; padding-top: 50px; }
    .login-box {
        background: white; padding: 40px; border-radius: 24px; width: 400px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); text-align: center;
    }
    
    /* Header Dashboard Sejajar */
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.3rem; margin: 0;
    }
    
    /* Metric Card */
    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #10b981;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE (LOAD & SAVE)
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
            if list(df.columns) != cols: return pd.DataFrame(columns=cols)
            return df
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def get_list_kelas():
    return [f"{tk}-{chr(i)}" for tk in ["X", "XI", "XII"] for i in range(ord('A'), ord('K'))]

# 4. SISTEM AUTHENTICATION
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("logo_uks.png", width=120) 
        st.markdown("<h2 style='color:#064e3b; margin-top:10px;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; margin-bottom:25px;'>Sistem Manajemen UKS Digital</p>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="adminuks", label_visibility="collapsed")
        pw = st.text_input("Password", type="password", placeholder="man1sukabumi", label_visibility="collapsed")
        
        if st.button("Masuk ke Sistem", use_container_width=True):
            if user == "adminuks" and pw == "man1sukabumi":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Akses Ditolak")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR MENU
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=80) 
        st.markdown("<h4 style='color:#064e3b;'>MAN 1 SUKABUMI</h4></div>---", unsafe_allow_html=True)
        menu = st.radio("Navigasi:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])
        st.markdown("<div style='height: 15vh;'></div>---", unsafe_allow_html=True)
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # 6. HALAMAN DASHBOARD
    if menu == "📊 Dashboard":
        col_h1, col_h2 = st.columns([0.1, 0.9])
        with col_h1: st.image("logo_uks.png", width=60)
        with col_h2: st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
        st.divider()

        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        df_k = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card"><h5>Kunjungan</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><h5>Kegiatan</h5><h2>{len(df_k)}</h2></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><h5>Jenis Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card"><h5>Status</h5><h2 style="color:#10b981;">ONLINE</h2></div>', unsafe_allow_html=True)

        st.markdown("### 📈 Statistik Kunjungan Siswa")
        if not df_p.empty:
            df_p['Waktu'] = pd.to_datetime(df_p['Waktu'], errors='coerce')
            df_p = df_p.dropna(subset=['Waktu'])
            if not df_p.empty:
                chart_data = df_p.groupby(df_p['Waktu'].dt.date).size()
                st.area_chart(chart_data, color="#10b981")
        else: st.info("Data kunjungan masih kosong.")

# 7. HALAMAN INPUT PASIEN (FIX: NAMA OTOMATIS BERUBAH SAAT KELAS DIGANTI)
    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>📝 Registrasi Pasien</h1>", unsafe_allow_html=True)
        df_s = load_data("siswa", ["nama_siswa", "kelas"])
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])

        with st.expander("➕ Tambah Master Data Siswa Baru"):
            with st.form("f_siswa", clear_on_submit=True):
                ns = st.text_input("Nama Lengkap Siswa")
                ks = st.selectbox("Pilih Kelas", get_list_kelas(), key="master_ks")
                if st.form_submit_button("Simpan Siswa"):
                    if ns:
                        df_s = pd.concat([df_s, pd.DataFrame([[ns, ks]], columns=df_s.columns)], ignore_index=True)
                        save_data(df_s, "siswa"); st.success(f"{ns} terdaftar!"); st.rerun()

        st.subheader("Catat Kunjungan Baru")
        
        # PILIH KELAS (Tanpa Form agar reaktif)
        pilih_kls = st.selectbox("1. Pilih Kelas", get_list_kelas(), key="filter_kelas")
        
        # Filter Nama berdasarkan Kelas yang dipilih di atas
        names_in_class = df_s[df_s['kelas'] == pilih_kls]['nama_siswa'].unique().tolist()
        names_in_class = sorted(names_in_class)

        with st.form("f_kunjungan", clear_on_submit=True):
            if names_in_class:
                # Menambahkan KEY dinamis berdasarkan 'pilih_kls' agar widget reset saat kelas pindah
                nama_psn = st.selectbox("2. Pilih Nama Siswa", names_in_class, key=f"select_nama_{pilih_kls}")
                keluhan = st.text_area("3. Keluhan")
                tindakan = st.text_input("4. Tindakan")
                
                if st.form_submit_button("➕ Simpan Kunjungan"):
                    if keluhan:
                        waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
                        new_p = pd.DataFrame([[waktu, nama_psn, pilih_kls, keluhan, tindakan]], columns=df_p.columns)
                        save_data(pd.concat([df_p, new_p], ignore_index=True), "pasien")
                        st.success(f"Kunjungan {nama_psn} berhasil dicatat!"); st.rerun()
                    else:
                        st.error("Keluhan harus diisi!")
            else:
                st.warning(f"⚠️ Belum ada data siswa di kelas {pilih_kls}. Daftarkan siswa terlebih dahulu di menu atas.")
                st.form_submit_button("Simpan Kunjungan", disabled=True)

    # 8. HALAMAN STOK OBAT
    elif menu == "💊 Stok Obat":
        st.markdown("<h1 class='main-header'>💊 Inventaris Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        with st.expander("➕ Tambah / Update Stok", expanded=True):
            with st.form("f_stok", clear_on_submit=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1: on = st.text_input("Nama Obat")
                with c2: js = st.number_input("Jumlah", min_value=0)
                with c3: us = st.selectbox("Satuan", ["Tablet", "Strip", "Pcs", "Botol", "Tube", "Sachet", "Kapsul", "Kaplet", "Pot", "Box", "Blister", "mL", "Unit"])
                if st.form_submit_button("➕ Simpan ke Inventaris"):
                    if on:
                        if on in df_o['Obat'].values:
                            df_o.loc[df_o['Obat'] == on, ['Stok', 'Satuan']] = [js, us]
                        else:
                            df_o = pd.concat([df_o, pd.DataFrame([[on, js, us]], columns=df_o.columns)], ignore_index=True)
                        save_data(df_o, "stok"); st.success("Stok diperbarui!"); st.rerun()
        st.dataframe(df_o, use_container_width=True)

    # 9. HALAMAN KEGIATAN
    elif menu == "📅 Kegiatan":
        st.markdown("<h1 class='main-header'>📅 Laporan Kegiatan</h1>", unsafe_allow_html=True)
        df_k = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
        with st.form("f_keg", clear_on_submit=True):
            tgl = st.date_input("Tanggal")
            keg = st.text_input("Nama Kegiatan")
            pes = st.number_input("Jumlah Peserta", min_value=0)
            ket = st.text_area("Keterangan")
            if st.form_submit_button("➕ Simpan Kegiatan"):
                if keg:
                    new_k = pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df_k.columns)
                    save_data(pd.concat([df_k, new_k], ignore_index=True), "kegiatan")
                    st.success("Kegiatan tersimpan!"); st.rerun()
        st.dataframe(df_k, use_container_width=True)

    # 10. KELOLA DATA
    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>📥 Manajemen Data</h1>", unsafe_allow_html=True)
        for k in ["pasien", "stok", "kegiatan", "siswa"]:
            d = load_data(k, ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"] if k=="pasien" else [])
            if not d.empty:
                with st.expander(f"Data {k.capitalize()}"):
                    st.download_button(f"📥 Download {k}.csv", d.to_csv(index=False), f"{k}.csv", "text/csv")
                    if st.button(f"🗑️ Hapus Baris Terakhir {k}"):
                        save_data(d[:-1], k); st.rerun()
                    st.dataframe(d, use_container_width=True)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | UKS Digital System")
