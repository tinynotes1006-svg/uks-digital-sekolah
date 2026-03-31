import streamlit as st
import pandas as pd
import os
import shutil
import pytz
import re
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
        font-weight: 800; font-size: 2.3rem; margin-bottom: 1rem;
    }
    .metric-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-top: 4px solid #10b981;
        text-align: center;
    }
    .login-box {
        background: white; padding: 2rem; border-radius: 20px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE & UTILITAS
FILES = {
    "pasien": "data_pasien.csv", 
    "stok": "data_obat.csv", 
    "kegiatan": "data_kegiatan.csv", 
    "siswa": "db_siswa.csv",
    "kesehatan": "data_kesehatan.csv"
}

def load_data(key):
    cols_map = {
        "pasien": ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"],
        "stok": ["Obat", "Stok", "Satuan", "Terakhir Update"],
        "kegiatan": ["Tanggal", "Kegiatan", "Peserta", "Keterangan", "Foto"],
        "siswa": ["nama_siswa", "kelas"],
        "kesehatan": ["Tanggal", "Nama", "Kelas", "Berat Badan", "Tinggi Badan", "Tensi", "Keterangan"]
    }
    cols = cols_map.get(key, [])
    
    if os.path.exists(FILES[key]):
        try:
            df = pd.read_csv(FILES[key])
            for col in cols:
                if col not in df.columns: df[col] = "-"
            return df[cols]
        except:
            return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def save_data(df, key):
    df.to_csv(FILES[key], index=False)

def get_list_kelas():
    # Menghasilkan A sampai K (ord 'L' adalah batas eksklusif)
    return [f"{tk}-{chr(i)}" for tk in ["X", "XI", "XII"] for i in range(ord('A'), ord('L'))]

# 4. SISTEM LOGIN
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("logo_uks.png", width=120) 
        st.markdown("<h2 style='color:#064e3b; margin-top:10px;'>MAN 1 KOTA SUKABUMI</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b;'>SISTEM UKS DIGITAL</p>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Username")
        pw = st.text_input("Password", type="password", placeholder="Password")
        if st.button("Masuk Sekarang", use_container_width=True):
            if user == "uksman1ksi" and pw == "man1kotsi":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Akses Ditolak: Username/Password Salah")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=80) 
        st.markdown("<h4 style='color:#064e3b;'>MAN 1 KOTA SUKABUMI</h4></div>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Menu Utama:", ["📊 Dashboard", "📝 Input Pasien", "🩺 Data Kesehatan", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])
        st.markdown("---")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # 6. DASHBOARD
    if menu == "📊 Dashboard":
        c_h1, c_h2 = st.columns([0.1, 0.9])
        with c_h1: st.image("logo_uks.png", width=110)
        with c_h2: st.markdown("<h1 class='main-header'>Dashboard UKS Digital</h1>", unsafe_allow_html=True)
        
        df_p = load_data("pasien")
        df_o = load_data("stok")
        df_k = load_data("kegiatan")
        df_kes = load_data("kesehatan")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f'<div class="metric-card"><h5>Kunjungan</h5><h2>{len(df_p)}</h2></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><h5>Pemeriksaan</h5><h2>{len(df_kes)}</h2></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><h5>Kegiatan</h5><h2>{len(df_k)}</h2></div>', unsafe_allow_html=True)
        with m4: st.markdown(f'<div class="metric-card"><h5>Jenis Obat</h5><h2>{len(df_o)}</h2></div>', unsafe_allow_html=True)
        
        st.markdown("### 📈 Statistik Kunjungan")
        if not df_p.empty:
            df_p['Waktu'] = pd.to_datetime(df_p['Waktu'], errors='coerce')
            chart_data = df_p.dropna(subset=['Waktu']).groupby(df_p['Waktu'].dt.date).size()
            st.area_chart(chart_data, color="#10b981")

    # 7. INPUT PASIEN
    elif menu == "📝 Input Pasien":
        st.markdown("<h1 class='main-header'>📝 Registrasi Pasien</h1>", unsafe_allow_html=True)
        df_s = load_data("siswa")
        df_p = load_data("pasien")

        with st.expander("➕ Tambah Master Data Siswa Baru"):
            with st.form("f_s", clear_on_submit=True):
                ns = st.text_input("Nama Lengkap Siswa")
                ks = st.selectbox("Pilih Kelas", get_list_kelas())
                if st.form_submit_button("Daftarkan Siswa"):
                    if ns:
                        new_s = pd.DataFrame([[ns, ks]], columns=df_s.columns)
                        save_data(pd.concat([df_s, new_s], ignore_index=True), "siswa")
                        st.success("Siswa Berhasil Terdaftar!"); st.rerun()

        st.subheader("Input Kunjungan UKS")
        pilih_kls = st.selectbox("1. Pilih Kelas", get_list_kelas())
        names = sorted(df_s[df_s['kelas'] == pilih_kls]['nama_siswa'].unique().tolist())

        with st.form("f_p", clear_on_submit=True):
            if names:
                c1, c2 = st.columns(2)
                with c1: tgl_kunj = st.date_input("2. Tanggal Kunjungan", datetime.now())
                with c2: n_psn = st.selectbox("3. Pilih Nama Siswa", names)
                
                kel = st.text_area("4. Keluhan / Gejala")
                tin = st.text_input("5. Tindakan / Obat yang diberikan")
                
                if st.form_submit_button("➕ Simpan Kunjungan"):
                    wkt_str = f"{tgl_kunj} {datetime.now().strftime('%H:%M')}"
                    new_row = pd.DataFrame([[wkt_str, n_psn, pilih_kls, kel, tin]], columns=df_p.columns)
                    save_data(pd.concat([df_p, new_row], ignore_index=True), "pasien")
                    st.success("Data Kunjungan Berhasil Disimpan!"); st.rerun()
            else:
                st.warning(f"Belum ada data siswa di kelas {pilih_kls}. Silakan tambah di expander atas.")
                st.form_submit_button("Simpan", disabled=True)

    # 8. DATA KESEHATAN (MENU BARU)
    elif menu == "🩺 Data Kesehatan":
        st.markdown("<h1 class='main-header'>🩺 Data Kesehatan Siswa</h1>", unsafe_allow_html=True)
        df_s = load_data("siswa")
        df_kes = load_data("kesehatan")

        with st.form("f_kes", clear_on_submit=True):
            st.subheader("Input Pemeriksaan Fisik")
            c1, c2 = st.columns(2)
            with c1:
                tgl_periksa = st.date_input("Tanggal Pemeriksaan")
                pilih_kls = st.selectbox("Kelas", get_list_kelas())
            with c2:
                names = sorted(df_s[df_s['kelas'] == pilih_kls]['nama_siswa'].unique().tolist())
                n_siswa = st.selectbox("Nama Siswa", names if names else ["Data Siswa Kosong"])
            
            cc1, cc2, cc3 = st.columns(3)
            with cc1: bb = st.number_input("Berat Badan (kg)", min_value=0.0, step=0.1)
            with cc2: tb = st.number_input("Tinggi Badan (cm)", min_value=0.0, step=0.1)
            with cc3: tensi = st.text_input("Tekanan Darah (Tensi)", placeholder="contoh: 120/80")
            
            ket_kes = st.text_area("Catatan / Keterangan Kesehatan")
            
            if st.form_submit_button("💾 Simpan Pemeriksaan"):
                if names:
                    new_data = pd.DataFrame([[str(tgl_periksa), n_siswa, pilih_kls, bb, tb, tensi, ket_kes]], columns=df_kes.columns)
                    save_data(pd.concat([df_kes, new_data], ignore_index=True), "kesehatan")
                    st.success("Data Kesehatan Berhasil Dicatat!"); st.rerun()
                else:
                    st.error("Gagal: Nama siswa tidak valid.")

        st.markdown("---")
        st.subheader("📋 Catatan Riwayat Kesehatan Terkini")
        st.dataframe(df_kes.iloc[::-1], use_container_width=True, hide_index=True)

    # 9. STOK OBAT
    elif menu == "💊 Stok Obat":
        st.markdown("<h1 class='main-header'>💊 Manajemen Stok Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok")
        
        with st.form("f_o", clear_on_submit=True):
            st.subheader("Update / Tambah Stok")
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                list_obat = df_o['Obat'].unique().tolist() if not df_o.empty else []
                on = st.selectbox("Pilih Obat", ["+ Tambah Baru"] + list_obat)
                on_baru = st.text_input("Nama Obat Baru (Jika tambah baru)")
            with c2:
                js = st.number_input("Jumlah", min_value=0)
            with c3:
                us = st.selectbox("Satuan", ["Tablet", "Strip", "Pcs", "Botol", "Sachet", "Box"])

            if st.form_submit_button("💾 Simpan Stok"):
                tz = pytz.timezone('Asia/Jakarta')
                wkt_upd = datetime.now(tz).strftime("%d/%m/%Y %H:%M")
                final_name = on_baru if on == "+ Tambah Baru" else on
                
                if final_name:
                    if on != "+ Tambah Baru": df_o = df_o[df_o['Obat'] != on]
                    new_o = pd.DataFrame([[final_name, js, us, wkt_upd]], columns=df_o.columns)
                    save_data(pd.concat([df_o, new_o], ignore_index=True), "stok")
                    st.success(f"Stok {final_name} diperbarui!"); st.rerun()

        st.dataframe(df_o.sort_values("Obat"), use_container_width=True, hide_index=True)

    # 10. KEGIATAN
    elif menu == "📅 Kegiatan":
        st.markdown("<h1 class='main-header'>📅 Laporan Kegiatan UKS</h1>", unsafe_allow_html=True)
        if not os.path.exists("uploads"): os.makedirs("uploads")
        df_k = load_data("kegiatan")
        
        with st.form("f_k", clear_on_submit=True):
            tgl_k = st.date_input("Tanggal Kegiatan")
            nama_k = st.text_input("Nama Kegiatan")
            peserta = st.number_input("Jumlah Peserta", min_value=0)
            ket_k = st.text_area("Detail Keterangan")
            foto = st.file_uploader("Upload Dokumentasi", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("➕ Simpan Laporan"):
                if nama_k:
                    fname = "No Photo"
                    if foto:
                        clean_name = re.sub(r'[^\w\s-]', '', nama_k).strip().replace(' ', '_')
                        fname = f"{tgl_k}_{clean_name}.png"
                        with open(os.path.join("uploads", fname), "wb") as f:
                            f.write(foto.getbuffer())
                    
                    new_k = pd.DataFrame([[str(tgl_k), nama_k, peserta, ket_k, fname]], columns=df_k.columns)
                    save_data(pd.concat([df_k, new_k], ignore_index=True), "kegiatan")
                    st.success("Laporan Kegiatan Tersimpan!"); st.rerun()

        # Riwayat Visual
        for _, row in df_k.iloc[::-1].iterrows():
            with st.expander(f"{row['Tanggal']} - {row['Kegiatan']}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    if row['Foto'] != "No Photo" and os.path.exists(f"uploads/{row['Foto']}"):
                        st.image(f"uploads/{row['Foto']}")
                    else: st.caption("Tidak ada foto.")
                with col2:
                    st.write(f"**Peserta:** {row['Peserta']} orang")
                    st.info(row['Keterangan'])

    # 11. KELOLA DATA
    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>📥 Manajemen Database</h1>", unsafe_allow_html=True)
        tabs = st.tabs(["🏥 Pasien", "🩺 Kesehatan", "💊 Stok", "📅 Kegiatan", "👥 Siswa"])
        
        # Helper untuk hapus data
        def render_tab(tab_idx, key, label_col):
            with tabs[tab_idx]:
                df = load_data(key)
                st.download_button(f"📥 Unduh CSV {key}", df.to_csv(index=False), f"data_{key}.csv", "text/csv")
                if not df.empty:
                    idx = st.selectbox(f"Pilih {key} untuk dihapus:", range(len(df)), 
                                      format_func=lambda x: f"{df.iloc[x][label_col]}")
                    if st.button(f"❌ Hapus Data", key=f"btn_{key}"):
                        if key == "kegiatan" and df.iloc[idx]['Foto'] != "No Photo":
                            p = f"uploads/{df.iloc[idx]['Foto']}"
                            if os.path.exists(p): os.remove(p)
                        df = df.drop(df.index[idx])
                        save_data(df, key)
                        st.rerun()
                st.dataframe(df, use_container_width=True)

        render_tab(0, "pasien", "Nama")
        render_tab(1, "kesehatan", "Nama")
        render_tab(2, "stok", "Obat")
        render_tab(3, "kegiatan", "Kegiatan")
        render_tab(4, "siswa", "nama_siswa")

st.markdown("---")
st.caption("© 2026 MAN 1 Kota Sukabumi | UKS Digital System")
