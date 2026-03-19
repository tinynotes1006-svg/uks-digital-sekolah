import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. KONEKSI GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    # Definisi kolom agar tidak terjadi KeyError jika Sheets kosong
    cols_map = {
        "pasien": ["Waktu", "Nama", "Kelas", "Keluhan", "Tindakan"],
        "stok": ["Obat", "Stok", "Satuan"],
        "kegiatan": ["Tanggal", "Kegiatan", "Peserta", "Keterangan"],
        "siswa": ["nama_siswa", "kelas"]
    }
    try:
        df = conn.read(worksheet=sheet_name, ttl="0")
        if df is None or df.empty:
            return pd.DataFrame(columns=cols_map[sheet_name])
        return df
    except:
        return pd.DataFrame(columns=cols_map[sheet_name])

def save_data(df, sheet_name):
    conn.update(worksheet=sheet_name, data=df)
    st.cache_data.clear()

# 3. SIDEBAR MENU
with st.sidebar:
    st.markdown("### UKS MAN 1 KOTA SUKABUMI")
    menu = st.radio("Menu:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])

# 4. DASHBOARD (DIPERBAIKI AGAR TIDAK ERROR 'WAKTU')
if menu == "📊 Dashboard":
    st.title("📊 Dashboard Utama")
    df_p = load_data("pasien")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Kunjungan", len(df_p))
    col2.metric("Kegiatan", len(load_data("kegiatan")))
    col3.metric("Jenis Obat", len(load_data("stok")))

    if not df_p.empty and 'Waktu' in df_p.columns:
        st.subheader("📈 Statistik Kunjungan")
        df_p['Waktu'] = pd.to_datetime(df_p['Waktu'], errors='coerce')
        df_p = df_p.dropna(subset=['Waktu'])
        if not df_p.empty:
            chart_data = df_p.groupby(df_p['Waktu'].dt.date).size()
            st.area_chart(chart_data)

# 5. INPUT PASIEN (FIX NAMA BERDASARKAN KELAS)
elif menu == "📝 Input Pasien":
    st.title("📝 Registrasi Pasien")
    df_s = load_data("siswa")
    df_p = load_data("pasien")
    
    with st.expander("➕ Tambah Master Siswa"):
        with st.form("f_s"):
            ns = st.text_input("Nama Lengkap")
            ks = st.selectbox("Kelas", [f"X-{i}" for i in range(1,11)]) # Sesuaikan kelas Anda
            if st.form_submit_button("Simpan Siswa"):
                new_s = pd.DataFrame([[ns, ks]], columns=df_s.columns)
                save_data(pd.concat([df_s, new_s], ignore_index=True), "siswa")
                st.success("Siswa Terdaftar!"); st.rerun()

    pilih_kls = st.selectbox("Pilih Kelas", df_s['kelas'].unique() if not df_s.empty else ["Belum Ada Data"])
    names = df_s[df_s['kelas'] == pilih_kls]['nama_siswa'].tolist()
    
    with st.form("f_p"):
        nama = st.selectbox("Nama Siswa", names if names else ["Kosong"])
        kel = st.text_area("Keluhan")
        tin = st.text_input("Tindakan")
        if st.form_submit_button("Simpan Kunjungan"):
            wkt = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_p = pd.DataFrame([[wkt, nama, pilih_kls, kel, tin]], columns=df_p.columns)
            save_data(pd.concat([df_p, new_p], ignore_index=True), "pasien")
            st.success("Tersimpan!"); st.rerun()

# 6. KEGIATAN (FIX VALUE ERROR)
elif menu == "📅 Kegiatan":
    st.title("📅 Laporan Kegiatan")
    df_k = load_data("kegiatan")
    with st.form("f_k"):
        tgl = st.date_input("Tanggal")
        keg = st.text_input("Acara")
        pes = st.number_input("Jumlah Peserta", min_value=0)
        ket = st.text_input("Keterangan") # Menambahkan kolom ke-4 agar tidak ValueError
        if st.form_submit_button("Simpan"):
            # Pastikan jumlah kolom (4) sama dengan yang ada di load_data
            new_k = pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df_k.columns)
            save_data(pd.concat([df_k, new_k], ignore_index=True), "kegiatan")
            st.success("Kegiatan Tersimpan!"); st.rerun()

# 7. KELOLA DATA (UNDUH SEMUA)
elif menu == "📥 Kelola Data":
    st.title("📥 Kelola Database")
    for k in ["pasien", "stok", "kegiatan", "siswa"]:
        df = load_data(k)
        st.write(f"### Data {k}")
        st.download_button(f"Unduh {k}.csv", df.to_csv(index=False), f"{k}.csv")
        st.dataframe(df)
