import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS MODERN
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

# 3. KONEKSI GOOGLE SHEETS
# Pastikan st.secrets sudah diisi di Dashboard Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        # ttl="0" memastikan data selalu fresh (tidak tersimpan di cache lama)
        return conn.read(worksheet=sheet_name, ttl="0")
    except:
        # Jika sheet kosong/error, return dataframe kosong sesuai kolomnya
        cols = {
            "pasien": ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"],
            "stok": ["Obat", "Stok", "Satuan"],
            "kegiatan": ["Tanggal", "Kegiatan", "Peserta", "Keterangan"],
            "siswa": ["nama_siswa", "kelas"]
        }
        return pd.DataFrame(columns=cols.get(sheet_name, []))

def save_data(df, sheet_name):
    conn.update(worksheet=sheet_name, data=df)
    st.cache_data.clear()

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
        if st.button("🚪 Keluar"):
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

    # 7. INPUT PASIEN (REAKTIF & CLOUD)
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
                        new_s = pd.DataFrame([[ns, ks]], columns=df_s.columns)
                        save_data(pd.concat([df_s, new_s], ignore_index=True), "siswa")
                        st.success("Siswa Terdaftar di Cloud!"); st.rerun()

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
                    st.success("Tersimpan ke Google Sheets!"); st.rerun()
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
                    new_o = pd.DataFrame([[on, js, us]], columns=df_o.columns)
                    save_data(pd.concat([df_o, new_o], ignore_index=True), "stok")
                    st.success("Stok Terupdate di Cloud!"); st.rerun()
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
                    new_k = pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df_k.columns)
                    save_data(pd.concat([df_k, new_k], ignore_index=True), "kegiatan")
                    st.success("Kegiatan Dicatat!"); st.rerun()
        st.dataframe(df_k, use_container_width=True)

    # 10. KELOLA DATA
    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>📥 Kelola & Unduh Data</h1>", unsafe_allow_html=True)
        tabs = st.tabs(["🏥 Pasien", "💊 Stok", "📅 Kegiatan", "👥 Siswa"])
        
        keys = ["pasien", "stok", "kegiatan", "siswa"]
        for i, k in enumerate(keys):
            with tabs[i]:
                df = load_data(k)
                st.download_button(f"📥 Download {k}.csv", df.to_csv(index=False), f"{k}.csv", "text/csv")
                if st.button(f"🗑️ Hapus Baris Terakhir {k.capitalize()}"):
                    if not df.empty:
                        save_data(df[:-1], k)
                        st.rerun()
                st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | UKS Digital Cloud System")
