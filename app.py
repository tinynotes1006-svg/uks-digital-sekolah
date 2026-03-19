import streamlit as st
import pandas as pd
import os
import shutil # Tambahkan ini di baris paling atas bersama import lainnya
import pytz # Tambahkan ini
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
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI DATABASE
FILES = {
    "pasien": "data_pasien.csv", 
    "stok": "data_obat.csv", 
    "kegiatan": "data_kegiatan.csv", 
    "siswa": "db_siswa.csv"
}

def load_data(key):
    cols_map = {
        "pasien": ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"],
        "stok": ["Obat", "Stok", "Satuan", "Terakhir Update"], # Pastikan ada 4 kolom
        "kegiatan": ["Tanggal", "Kegiatan", "Peserta", "Keterangan", "Foto"],
        "siswa": ["nama_siswa", "kelas"]
    }
    cols = cols_map.get(key, [])
    
    if os.path.exists(FILES[key]):
        try:
            df = pd.read_csv(FILES[key])
            # LOGIKA PENYEMBUH: Jika kolom kurang, tambahkan otomatis
            for col in cols:
                if col not in df.columns:
                    df[col] = "-" # Isi default untuk kolom baru
            
            # Kembalikan dataframe sesuai urutan kolom di cols_map
            return df[cols]
        except:
            return pd.DataFrame(columns=cols)
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
        st.markdown("<div class='sekolah-sub-login'>SISTEM UKS DIGITAL</div>", unsafe_allow_html=True)
        
        user = st.text_input("Username", placeholder="Username")
        pw = st.text_input("Password", type="password", placeholder="password")
        if st.button("Masuk", use_container_width=True):
            if user == "adminuks" and pw == "123456":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Akses Ditolak")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 5. SIDEBAR
    with st.sidebar:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.image("logo_sekolah.png", width=80) 
        st.markdown("<h4 style='color:#064e3b;'>MAN 1 KOTA SUKABUMI</h4></div>______________", unsafe_allow_html=True)
        menu = st.radio("Menu Utama:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])
        if st.button("🚪 Keluar Sistem"):
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
        st.markdown("<h1 class='main-header'>💊 Manajemen Stok Obat</h1>", unsafe_allow_html=True)
        df_o = load_data("stok")
        
        with st.form("f_o", clear_on_submit=True):
            st.subheader("Input / Update Stok")
            c1, c2, c3 = st.columns([2, 1, 1])
            
            with c1:
                # Ambil daftar obat yang ada
                list_obat = df_o['Obat'].unique().tolist() if not df_o.empty else []
                on = st.selectbox("Pilih Obat", ["+ Tambah Baru"] + list_obat)
                on_baru = st.text_input("Nama Obat Baru (jika pilih Tambah Baru)")
                
            with c2:
                js = st.number_input("Jumlah Stok", min_value=0)
                
            with c3:
                us = st.selectbox("Satuan", ["Tablet", "Strip", "Pcs", "Botol", "Sachet", "Kapsul"])

            if st.form_submit_button("💾 Simpan Data"):
                nama_final = on_baru if on == "+ Tambah Baru" else on
                # Kode baru (Zona Jakarta/WIB)
                    tz_jakarta = pytz.timezone('Asia/Jakarta')
                    tgl_update = datetime.now(tz_jakarta).strftime("%d/%m/%Y %H:%M")
                
                if nama_final:
                    # Jika update obat lama, hapus baris lamanya dulu
                    if on != "+ Tambah Baru":
                        df_o = df_o[df_o['Obat'] != on]
                    
                    # Buat data baru (4 kolom sesuai cols_map)
                    new_stok = pd.DataFrame([[nama_final, js, us, tgl_update]], columns=df_o.columns)
                    df_o = pd.concat([df_o, new_stok], ignore_index=True)
                    
                    save_data(df_o, "stok")
                    st.success(f"✅ Stok {nama_final} diperbarui!")
                    st.rerun()
                else:
                    st.error("Nama obat tidak boleh kosong!")

        st.markdown("---")
        st.subheader("📦 Data Inventaris UKS")
        if not df_o.empty:
            # Urutkan berdasarkan nama obat
            st.dataframe(df_o.sort_values("Obat"), use_container_width=True, hide_index=True)
        else:
            st.info("Stok masih kosong.")
   # 9. KEGIATAN
    elif menu == "📅 Kegiatan":
        st.markdown("<h1 class='main-header'>📅 Laporan Kegiatan</h1>", unsafe_allow_html=True)
        
        # Pastikan folder foto ada
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        df_k = load_data("kegiatan")
        
        with st.form("f_k", clear_on_submit=True):
            tgl = st.date_input("Tanggal")
            keg = st.text_input("Nama Kegiatan")
            pes = st.number_input("Jumlah Peserta", min_value=0)
            ket = st.text_area("Keterangan Kegiatan")
            
            # Widget Upload Foto
            uploaded_file = st.file_uploader("Pilih Foto Dokumentasi (JPG/PNG)", type=["jpg", "jpeg", "png"])
            
            if st.form_submit_button("➕ Simpan Kegiatan"):
                if keg:
                    file_name = "No Photo"
                    
                    if uploaded_file is not None:
                        # 1. Bersihkan nama kegiatan dari karakter yang dilarang di nama file (seperti / \ : * ? " < > |)
                        import re
                        keg_clean = re.sub(r'[^\w\s-]', '', keg).strip().replace(' ', '_')
                        
                        # 2. Ambil ekstensi file asli (.png atau .jpg)
                        extension = os.path.splitext(uploaded_file.name)[1]
                        
                        # 3. Gabungkan Tanggal + Nama Kegiatan
                        # Hasilnya misal: 2024-05-20_Pemeriksaan_Berkala.png
                        file_name = f"{tgl}_{keg_clean}{extension}"
                        
                        # Simpan ke folder uploads
                        with open(os.path.join("uploads", file_name), "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # Simpan data ke DataFrame
                    new_row = pd.DataFrame([[str(tgl), keg, pes, ket, file_name]], columns=df_k.columns)
                    df_updated = pd.concat([df_k, new_row], ignore_index=True)
                    save_data(df_updated, "kegiatan")
                    
                    st.success(f"✅ Berhasil! Foto disimpan sebagai: {file_name}")
                    st.rerun()
                    
                    # Membuat baris baru (Pastikan kolom pas dengan load_data)
                    new_row = pd.DataFrame([[str(tgl), keg, pes, ket, file_name]], columns=df_k.columns)
                    
                    # Gabungkan dan simpan
                    df_updated = pd.concat([df_k, new_row], ignore_index=True)
                    save_data(df_updated, "kegiatan")
                    
                    st.success("✅ Data dan Foto Berhasil Disimpan!")
                    st.rerun()
                else:
                    st.warning("⚠️ Nama kegiatan tidak boleh kosong.")

        st.markdown("---")
        st.subheader("📋 Riwayat Kegiatan")
        
        if not df_k.empty:
            # Tampilkan data terbaru di urutan paling atas (iloc[::-1])
            for index, row in df_k.iloc[::-1].iterrows():
                with st.expander(f"{row['Tanggal']} - {row['Kegiatan']}"):
                    col_foto, col_info = st.columns([1, 2])
                    
                    with col_foto:
                        path_foto = os.path.join("uploads", str(row['Foto']))
                        if row['Foto'] != "No Photo" and os.path.exists(path_foto):
                            st.image(path_foto, use_container_width=True)
                        else:
                            st.caption("📷 Tidak ada dokumentasi.")
                    
                    with col_info:
                        st.write(f"**Peserta:** {row['Peserta']} orang")
                        st.write(f"**Keterangan:**")
                        st.info(row['Keterangan'] if row['Keterangan'] else "-")
        else:
            st.info("Belum ada data kegiatan.")
   # 10. KELOLA DATA
    elif menu == "📥 Kelola Data":
        st.markdown("<h1 class='main-header'>📥 Kelola & Unduh Data</h1>", unsafe_allow_html=True)
        st.info("Di sini Anda dapat mengunduh semua database UKS atau menghapus data yang salah.")
        
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
            col_csv, col_zip = st.columns(2)
            
            with col_csv:
                st.download_button("📥 Download Data (CSV)", d_keg.to_csv(index=False), "data_kegiatan.csv", "text/csv", use_container_width=True)
            
            with col_zip:
                if os.path.exists("uploads") and os.listdir("uploads"):
                    import shutil
                    shutil.make_archive("backup_foto", 'zip', "uploads")
                    with open("backup_foto.zip", "rb") as fp:
                        st.download_button("🖼️ Download Foto (ZIP)", data=fp, file_name="foto_uks.zip", mime="application/zip", use_container_width=True)
                else:
                    st.button("🖼️ Belum Ada Foto", disabled=True, use_container_width=True)

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
