import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN & STYLE CSS
st.set_page_config(page_title="UKS Digital MAN 1 Kota Sukabumi", page_icon="🏥", layout="wide")

st.markdown("""
    <style>
    .logo-container { display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 5px; }
    .login-logo-img { width: 50px; height: 50px; object-fit: contain; }
    [data-testid="stSidebar"] { background-color: #004d40; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stButton>button { background-color: #00c853; color: white; border-radius: 8px; font-weight: bold; width: 100%; border: none; height: 3em; }
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
        try:
            return pd.read_csv(FILES[key])
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def list_kelas():
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))]
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))]
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))]
    return kx + kxi + kxii

# 3. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("###")
        # PERBAIKAN: Ganti 'username-github-anda' dengan username GitHub asli Anda
        USER_GH = "krisna-be" 
        REPO_GH = "uks-digital-sekolah"
        
        st.markdown(f"""
            <div class="logo-container">
                <img src="https://raw.githubusercontent.com/{USER_GH}/{REPO_GH}/main/logo_sekolah.png" class="login-logo-img">
                <img src="https://raw.githubusercontent.com/{USER_GH}/{REPO_GH}/main/logo_uks.png" class="login-logo-img">
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
                st.error("Login Gagal!")
else:
    # 4. SIDEBAR & MENU
    st.sidebar.markdown("<h3 style='text-align:center;'>🏥 MENU UTAMA</h3>", unsafe_allow_html=True)
    menu = st.sidebar.radio("Pilih Menu:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan Besar", "📥 Ekspor Data", "Keluar"])
    
    if menu == "Keluar":
        st.session_state.auth = False
        st.rerun()

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.markdown("<h2 class='main-header'>📊 RINGKASAN DATA</h2>", unsafe_allow_html=True)
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        c1, c2 = st.columns(2); c1.metric("Total Pasien", len(df_p)); c2.metric("Jenis Obat", len(df_o))
        st.dataframe(df_p.tail(5), use_container_width=True)

    # --- INPUT PASIEN ---
    elif menu == "📝 Input Pasien":
        st.markdown("<h2 class='main-header'>📝 CATAT KUNJUNGAN</h2>", unsafe_allow_html=True)
        df_siswa = load_data("siswa", ["nama_siswa", "kelas"])
        
        with st.expander("➕ Tambah Siswa Baru"):
            with st.form("tambah_siswa", clear_on_submit=True):
                n_baru = st.text_input("Nama Siswa"); k_baru = st.selectbox("Kelas", list_kelas())
                if st.form_submit_button("Simpan Siswa"):
                    if n_baru:
                        df_siswa = pd.concat([df_siswa, pd.DataFrame([[n_baru, k_baru]], columns=["nama_siswa", "kelas"])], ignore_index=True)
                        save_data(df_siswa, "siswa"); st.success("Tersimpan!"); st.rerun()

        with st.form("form_p", clear_on_submit=True):
            f_kelas = st.selectbox("Pilih Kelas", list_kelas())
            list_nama = df_siswa[df_siswa['kelas'] == f_kelas]['nama_siswa'].tolist()
            f_nama = st.selectbox("Pilih Nama", sorted(list_nama) if list_nama else ["Kosong"])
            f_kel = st.text_area("Keluhan"); f_tin = st.text_input("Tindakan")
            if st.form_submit_button("SIMPAN KUNJUNGAN"):
                if f_nama != "Kosong" and f_kel:
                    df = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
                    new_p = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), f_nama, f_kelas, f_kel, f_tin]], columns=df.columns)
                    save_data(pd.concat([df, new_p], ignore_index=True), "pasien")
                    st.success("Tersimpan!"); st.balloons()

    # --- STOK OBAT ---
    elif menu == "💊 Stok Obat":
        st.markdown("<h2 class='main-header'>💊 STOK OBAT</h2>", unsafe_allow_html=True)
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        with st.form("form_o", clear_on_submit=True):
            n_o = st.text_input("Obat"); j_o = st.number_input("Stok", min_value=0); s_o = st.selectbox("Satuan", ["Tablet", "Botol", "Pcs"])
            if st.form_submit_button("UPDATE"):
                if n_o in df_o['Obat'].values: df_o.loc[df_o['Obat'] == n_o, ['Stok', 'Satuan']] = [j_o, s_o]
                else: df_o = pd.concat([df_o, pd.DataFrame([[n_o, j_o, s_o]], columns=df_o.columns)], ignore_index=True)
                save_data(df_o, "stok"); st.success("Updated!")
        st.dataframe(df_o, use_container_width=True)

    # --- KEGIATAN BESAR ---
    elif menu == "📅 Kegiatan Besar":
        st.markdown("<h2 class='main-header'>📅 KEGIATAN UKS</h2>", unsafe_allow_html=True)
        with st.form("form_k", clear_on_submit=True):
            tgl = st.date_input("Tanggal"); keg = st.text_input("Kegiatan"); pes = st.number_input("Peserta", min_value=0); ket = st.text_area("Keterangan")
            if st.form_submit_button("SIMPAN KEGIATAN"):
                if keg:
                    df = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
                    new_k = pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df.columns)
                    save_data(pd.concat([df, new_k], ignore_index=True), "kegiatan")
                    st.success("Kegiatan Dicatat!")

    # --- EKSPOR DATA ---
    elif menu == "📥 Ekspor Data":
        st.markdown("<h2 class='main-header'>📥 DOWNLOAD DATA</h2>", unsafe_allow_html=True)
        for k in FILES:
            df = load_data(k, [])
            if not df.empty:
                st.download_button(f"Unduh {k.capitalize()}", df.to_csv(index=False), f"{k}.csv", "text/csv")
                st.dataframe(df)

st.markdown("---")
st.caption("© 2026 UKS MAN 1 Kota Sukabumi")
