import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS UNTUK TAMPILAN MODERN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    

/* Login Box Centering */
    .login-container { display: flex; justify-content: center; align-items: center; padding-top: 50px; }
    .login-box {
        background: white; padding: 45px; border-radius: 28px; width: 420px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0; text-align: center;
    }
    
    /* Styling Input Login */
    .stTextInput input {
        border-radius: 12px !important;
        padding: 12px !important;
        border: 1px solid #cbd5e1 !important
    }
    
    /* Dashboard Header */
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.5rem; text-align: center;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    
    /* Card */
    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #10b981;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE CSV
FILES = {"pasien": "data_pasien.csv", "stok": "data_stok.csv", "kegiatan": "data_kegiatan.csv", "siswa": "db_siswa.csv"}

def load_data(key, cols):
    if os.path.exists(FILES[key]):
        try: return pd.read_csv(FILES[key])
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def get_list_kelas():
    kx = [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))]
    kxi = [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))]
    kxii = [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))]
    return kx + kxi + kxii

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        # LOGO UKS DI TENAH (CENTERED)
        st.image("logo_uks.png", width=120) 
        
        st.markdown("<h2 style='color:#064e3b; margin-top:20px; margin-bottom:0;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; margin-bottom:30px; font-weight:500;'>Sistem Manajemen UKS Digital</p>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Username Admin", label_visibility="collapsed")
        pw = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
        
        st.write("") # Spasi tambahan
        if st.button("MASUK KE SISTEM", use_container_width=True):
            if user == "adminuks" and pw == "123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Akses Ditolak: Periksa Kembali Credential Anda.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR (HANYA LOGO SEKOLAH)
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=80) # Logo Sekolah Saja
        st.markdown("<h4 style='color:#064e3b; margin-top:10px;'>MAN 1 SUKABUMI</h4>", unsafe_allow_html=True)
        st.markdown("</div>---", unsafe_allow_html=True)
        
        menu = st.radio("Pilih Layanan:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan UKS", "📥 Ekspor & Kelola"])
        
        st.markdown("<div style='height: 20vh;'></div>---", unsafe_allow_html=True)
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # 6. KONTEN HALAMAN
    if menu == "📊 Dashboard":
        # HEADER DASHBOARD DENGAN LOGO UKS
        col_dash1, col_dash2, col_dash3 = st.columns([1, 3, 1])
        with col_dash2:
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            st.image("logo_uks.png", width=80) # Logo UKS Pindah ke Sini
            st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        
        st.write("---")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="metric-card"><h5>Total Pasien</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><h5>Varian Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><h5>Status</h5><h2 style="color:#10b981;">Online</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### 🕒 Riwayat Kunjungan Terbaru")
        st.dataframe(df_p.tail(10), use_container_width=True)

    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>Catat Kunjungan</h1>", unsafe_allow_html=True)
        # Sisa kode tetap sama...
        df_s = load_data("siswa", ["nama_siswa", "kelas"])
        with st.expander("➕ Tambah Master Data Siswa"):
            with st.form("add_siswa", clear_on_submit=True):
                ns = st.text_input("Nama Siswa")
                ks = st.selectbox("Kelas", get_list_kelas())
                if st.form_submit_button("Simpan Siswa"):
                    if ns:
                        df_s = pd.concat([df_s, pd.DataFrame([[ns, ks]], columns=["nama_siswa", "kelas"])], ignore_index=True)
                        save_data(df_s, "siswa"); st.success("Siswa ditambahkan!"); st.rerun()
        
        with st.form("input_p", clear_on_submit=True):
            kls = st.selectbox("Filter Kelas", get_list_kelas())
            list_n = df_s[df_s['kelas'] == kls]['nama_siswa'].tolist()
            nama = st.selectbox("Pilih Nama", sorted(list_n) if list_n else ["Data Kosong"])
            kel = st.text_area("Keluhan"); tin = st.text_input("Tindakan")
            if st.form_submit_button("Simpan Kunjungan"):
                if nama != "Data Kosong" and kel:
                    df = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
                    new_r = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), nama, kls, kel, tin]], columns=df.columns)
                    save_data(pd.concat([df, new_r], ignore_index=True), "pasien"); st.success("Berhasil Disimpan!")

    elif menu == "💊 Stok Obat":
        st.markdown("<h1 class='main-header'>Stok Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
        with st.form("stok_f", clear_on_submit=True):
            o_n = st.text_input("Nama Obat"); o_s = st.number_input("Jumlah", min_value=0); o_u = st.selectbox("Satuan", ["Tablet", "Botol", "Pcs"])
            if st.form_submit_button("Update Stok"):
                if o_n:
                    if o_n in df_o['Obat'].values: df_o.loc[df_o['Obat'] == o_n, ['Stok', 'Satuan']] = [o_s, o_u]
                    else: df_o = pd.concat([df_o, pd.DataFrame([[o_n, o_s, o_u]], columns=df_o.columns)], ignore_index=True)
                    save_data(df_o, "stok"); st.success("Stok diperbarui!")
        st.dataframe(df_o, use_container_width=True)

    elif menu == "📅 Kegiatan UKS":
        st.markdown("<h1 class='main-header'>Kegiatan Besar</h1>", unsafe_allow_html=True)
        with st.form("keg_f", clear_on_submit=True):
            k_t = st.date_input("Tanggal"); k_n = st.text_input("Kegiatan"); k_p = st.number_input("Peserta", min_value=0); k_k = st.text_area("Keterangan")
            if st.form_submit_button("Simpan Kegiatan"):
                if k_n:
                    df = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
                    save_data(pd.concat([df, pd.DataFrame([[str(k_t), k_n, k_p, k_k]], columns=df.columns)], ignore_index=True), "kegiatan"); st.success("Kegiatan dicatat!")

    elif menu == "📥 Ekspor & Kelola":
        st.markdown("<h1 class='main-header'>Kelola Data</h1>", unsafe_allow_html=True)
        for k in ["pasien", "stok", "kegiatan", "siswa"]:
            d = load_data(k, [])
            if not d.empty:
                with st.expander(f"Kelola {k.capitalize()}"):
                    st.download_button(f"📥 Download CSV {k}", d.to_csv(index=False), f"{k}.csv", "text/csv")
                    row = st.selectbox(f"Hapus {k}", d.index, key=f"del_{k}")
                    if st.button(f"🗑️ Hapus Permanen {k}", key=f"btn_{k}"):
                        d = d.drop(row).reset_index(drop=True)
                        save_data(d, k); st.success("Terhapus!"); st.rerun()
                    st.dataframe(d, use_container_width=True)

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | UKS Digital System")
