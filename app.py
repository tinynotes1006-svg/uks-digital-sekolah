import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime
import os
st.set_page_config(page_title="UKS Digital MAN 1", layout="wide")
conn = st.connection("supabase", type=SupabaseConnection)
# --- FUNGSI HELPER ---
def get_kelas_list():
    return [f"X-{chr(i)}" for i in range(ord('A'), ord('K'))] + \
           [f"XI-{chr(i)}" for i in range(ord('A'), ord('L'))] + \
           [f"XII-{chr(i)}" for i in range(ord('A'), ord('K'))]

# --- SESSION & LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login UKS MAN 1")
    if os.path.exists("logo_uks.png"): st.image("logo_uks.png", width=100)
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Masuk"):
        if u == "adminuks" and p == "man1sukabumi":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Salah!")
else:
    menu = st.sidebar.radio("Navigasi", ["📝 Input Pasien", "💊 Stok Obat", "📅 Kegiatan Besar", "📊 Laporan", "Keluar"])
    
    if menu == "Keluar":
        st.session_state.auth = False
        st.rerun()

    # 1. INPUT PASIEN
    if menu == "📝 Input Pasien":
        st.header("Form Kunjungan Harian")
        df_s = pd.DataFrame(conn.table("master_siswa").select("*").execute().data)
        c1, c2 = st.columns(2); kls = c1.selectbox("Kelas", get_kelas_list())
        n_list = df_s[df_s['kelas'] == kls]['nama_siswa'].tolist()
        nama = c2.selectbox("Nama Siswa", sorted(n_list) if n_list else ["Kosong"])
        
        with st.form("f_p"):
            kel, obt, pet = st.text_area("Keluhan"), st.text_input("Obat/Tindakan"), st.text_input("Petugas")
            if st.form_submit_button("Simpan"):
                conn.table("data_pasien").insert({"nama_siswa":nama, "kelas":kls, "keluhan":kel, "obat_tindakan":obt, "petugas":pet}).execute()
                st.success("Tersimpan!"); st.balloons()

    # 2. STOK OBAT
    elif menu == "💊 Stok Obat":
        st.header("Stok Obat")
        with st.form("f_o"):
            n, j, s = st.text_input("Nama Obat"), st.number_input("Jumlah", min_value=0), st.selectbox("Satuan", ["Tablet", "Pcs", "Botol", "Sachet"])
            if st.form_submit_button("Update Stok"):
                conn.table("stok_obat").upsert({"nama_obat":n, "jumlah":j, "satuan":s}).execute()
        st.table(pd.DataFrame(conn.table("stok_obat").select("*").execute().data))

    # 3. KEGIATAN BESAR (Donor Darah, dll)
    elif menu == "📅 Kegiatan Besar":
        st.header("Laporan Kegiatan UKS (Event)")
        with st.form("f_k"):
            tgl, nama_k, lok, jml, ket = st.date_input("Tanggal"), st.text_input("Nama Kegiatan"), st.text_input("Lokasi"), st.number_input("Peserta", min_value=0), st.text_area("Hasil")
            if st.form_submit_button("Simpan Kegiatan"):
                conn.table("kegiatan_uks").insert({"tanggal":str(tgl), "nama_kegiatan":nama_k, "lokasi":lok, "jumlah_peserta":jml, "keterangan":ket}).execute()
                st.success("Kegiatan Dicatat!")

    # 4. LAPORAN
    elif menu == "📊 Laporan":
        st.header("Pusat Laporan")
        tab1, tab2 = st.tabs(["Kunjungan Pasien", "Kegiatan Besar"])
        with tab1:
            df1 = pd.DataFrame(conn.table("data_pasien").select("*").execute().data)
            st.dataframe(df1); st.download_button("Download CSV", df1.to_csv(index=False), "pasien.csv")
        with tab2:
            df2 = pd.DataFrame(conn.table("kegiatan_uks").select("*").execute().data)
            st.dataframe(df2); st.download_button("Download CSV", df2.to_csv(index=False), "kegiatan.csv")
