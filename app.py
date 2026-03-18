import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. CSS CUSTOM UNTUK TAMPILAN MODERN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Card Statisik */
    .metric-card {
        background: white; padding: 24px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        border-bottom: 5px solid #10b981;
        text-align: center;
    }
    .metric-card h5 { color: #64748b; font-size: 0.9rem; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .metric-card h2 { color: #0f172a; font-size: 2.5rem; font-weight: 800; margin: 0; }
    
    /* Header Dashboard */
    .main-header {
        background: linear-gradient(90deg, #059669, #10b981);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 2.2rem; margin: 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
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
        st.markdown("<h4 style='color:#064e3b; margin-top:10px;'>MAN 1 KOTA SUKABUMI</h4>", unsafe_allow_html=True)
        st.markdown("</div>---", unsafe_allow_html=True)
        
        menu = st.radio("Pilih Layanan:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan UKS", "📥 Ekspor & Kelola"])
        
        st.markdown("<div style='height: 20vh;'></div>---", unsafe_allow_html=True)
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

# 4. SISTEM AUTH (Sederhana)
if 'auth' not in st.session_state: st.session_state.auth = True # Set True untuk preview langsung

# 5. SIDEBAR
with st.sidebar:
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image("logo_sekolah.png", width=80) 
    st.markdown("<h4 style='color:#064e3b; margin-top:10px;'>MAN 1 SUKABUMI</h4>", unsafe_allow_html=True)
    st.markdown("</div>---", unsafe_allow_html=True)
    menu = st.radio("Navigasi", ["📊 Dashboard Statistik", "📝 Registrasi Pasien", "💊 Inventaris Obat", "📅 Agenda Kegiatan"])

# 6. HALAMAN DASHBOARD UTAMA
if menu == "📊 Dashboard Statistik":
    # Header dengan Logo Samping Judul
    head_col1, head_col2 = st.columns([0.1, 0.9])
    with head_col1: st.image("logo_uks.png", width=60)
    with head_col2: st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Load Data untuk Hitung Metrik
    df_p = load_data("pasien", ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"])
    df_o = load_data("stok", ["Obat", "Stok", "Satuan"])
    df_k = load_data("kegiatan", ["Tanggal", "Kegiatan", "Peserta", "Keterangan"])
    
    # --- BARIS 1: TOTAL METRIK ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><h5>Total Kunjungan</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><h5>Total Kegiatan</h5><h2>{len(df_k)}</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><h5>Jenis Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><h5>Status Sistem</h5><h2 style="color:#10b981; font-size:1.8rem;">ONLINE</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BARIS 2: STATISTIK & AGENDA ---
    col_graph, col_agenda = st.columns([1.2, 0.8])
    
    with col_graph:
        st.markdown("### 📈 Statistik Kunjungan Siswa")
        if not df_p.empty:
            # Mengolah data untuk grafik per tanggal
            df_p['Waktu'] = pd.to_datetime(df_p['Waktu']).dt.date
            chart_data = df_p.groupby('Waktu').size().reset_index(name='Jumlah')
            st.area_chart(chart_data.set_index('Waktu'), color="#10b981")
        else:
            st.info("Belum ada data statistik untuk ditampilkan.")

    with col_agenda:
        st.markdown("### 📅 Agenda Kegiatan Terdekat")
        if not df_k.empty:
            # Tampilkan 5 kegiatan terbaru
            df_k_view = df_k.sort_values(by="Tanggal", ascending=False).head(5)
            for i, row in df_k_view.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background:white; padding:15px; border-radius:12px; margin-bottom:10px; border-left:4px solid #059669;">
                        <small style="color:#64748b;">{row['Tanggal']}</small><br>
                        <strong style="color:#0f172a;">{row['Kegiatan']}</strong><br>
                        <small style="color:#10b981;">{row['Peserta']} Peserta</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write("Tidak ada agenda kegiatan.")

    # --- BARIS 3: TABEL DETAIL ---
    st.markdown("### 🕒 Riwayat Kunjungan Terakhir")
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
