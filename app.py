import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="UKS Digital MAN 1", page_icon="🏥", layout="wide")

# 2. KONEKSI GOOGLE SHEETS
# Menggunakan penanganan error agar aplikasi tidak crash jika koneksi gagal
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Koneksi database gagal. Periksa 'Secrets' di Dashboard Streamlit.")
    st.stop()

def load_data(sheet_name):
    # Struktur kolom standar untuk mencegah KeyError
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
        # Memastikan semua kolom yang dibutuhkan ada
        for col in cols_map[sheet_name]:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=cols_map[sheet_name])

def save_data(df, sheet_name):
    conn.update(worksheet=sheet_name, data=df)
    st.cache_data.clear()

# 3. SIDEBAR MENU
with st.sidebar:
    st.markdown("### UKS MAN 1 KOTA SUKABUMI")
    menu = st.radio("Navigasi:", ["📊 Dashboard", "📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan", "📥 Kelola Data"])

# 4. DASHBOARD (FIX ERROR WAKTU)
if menu == "📊 Dashboard":
    st.markdown("<h1 style='color:#10b981;'>📊 Dashboard UKS</h1>", unsafe_allow_html=True)
    df_p = load_data("pasien")
    df_o = load_data("stok")
    df_k = load_data("kegiatan")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Pasien", len(df_p))
    c2.metric("Total Kegiatan", len(df_k))
    c3.metric("Jenis Obat", len(df_o))

    st.markdown("### 📈 Statistik Kunjungan")
    # Cek apakah kolom Waktu ada dan tidak kosong
    if not df_p.empty and "Waktu" in df_p.columns:
        df_p['Waktu'] = pd.to_datetime(df_p['Waktu'], errors='coerce')
        df_plot = df_p.dropna(subset=['Waktu'])
        if not df_plot.empty:
            chart_data = df_plot.groupby(df_plot['Waktu'].dt.date).size()
            st.area_chart(chart_data, color="#10b981")
        else:
            st.info("Belum ada data statistik untuk ditampilkan.")
    else:
        st.info("Data kunjungan masih kosong.")

# 5. INPUT PASIEN (FIX FILTER NAMA)
elif menu == "📝 Input Pasien":
    st.title("📝 Registrasi Pasien")
    df_s = load_data("siswa")
    df_p = load_data("pasien")

    with st.expander("➕ Tambah Siswa ke Database"):
        with st.form("add_siswa"):
            n_baru = st.text_input("Nama Siswa")
            k_baru = st.selectbox("Kelas", [f"X-{i}" for i in range(1,11)] + [f"XI-{i}" for i in range(1,11)])
            if st.form_submit_button("Simpan Siswa"):
                new_row = pd.DataFrame([[n_baru, k_baru]], columns=["nama_siswa", "kelas"])
                save_data(pd.concat([df_s, new_row], ignore_index=True), "siswa")
                st.success("Siswa berhasil didaftarkan!"); st.rerun()

    # Filter Reaktif
    list_kls = sorted(df_s['kelas'].unique()) if not df_s.empty else []
    pilih_kls = st.selectbox("1. Pilih Kelas", list_kls if list_kls else ["Data Kosong"])
    
    names = sorted(df_s[df_s['kelas'] == pilih_kls]['nama_siswa'].tolist()) if list_kls else []

    with st.form("input_kunjungan", clear_on_submit=True):
        nama_p = st.selectbox("2. Pilih Nama Siswa", names if names else ["Tidak ada siswa"])
        kel = st.text_area("3. Keluhan")
        tin = st.text_input("4. Tindakan")
        if st.form_submit_button("➕ Simpan Kunjungan"):
            if names and kel:
                wkt = datetime.now().strftime("%Y-%m-%d %H:%M")
                new_entry = pd.DataFrame([[wkt, nama_p, pilih_kls, kel, tin]], columns=df_p.columns)
                save_data(pd.concat([df_p, new_entry], ignore_index=True), "pasien")
                st.success("Kunjungan dicatat!"); st.rerun()

# 6. KEGIATAN (FIX VALUE ERROR)
elif menu == "📅 Kegiatan":
    st.title("📅 Laporan Kegiatan")
    df_k = load_data("kegiatan")
    with st.form("form_keg"):
        tgl = st.date_input("Tanggal")
        keg = st.text_input("Nama Acara")
        pes = st.number_input("Jumlah Peserta", min_value=0)
        ket = st.text_input("Keterangan Tambahan")
        if st.form_submit_button("Simpan Kegiatan"):
            # Menjamin 4 kolom sesuai struktur database
            new_row_k = pd.DataFrame([[str(tgl), keg, pes, ket]], columns=df_k.columns)
            save_data(pd.concat([df_k, new_row_k], ignore_index=True), "kegiatan")
            st.success("Kegiatan berhasil disimpan!"); st.rerun()
    st.dataframe(df_k, use_container_width=True)

# 7. KELOLA DATA
elif menu == "📥 Kelola Data":
    st.title("📥 Download Database")
    for k in ["pasien", "stok", "kegiatan", "siswa"]:
        df_view = load_data(k)
        st.subheader(f"Data {k.capitalize()}")
        st.download_button(f"Download {k}.csv", df_view.to_csv(index=False), f"{k}.csv")
        st.dataframe(df_view, use_container_width=True)
