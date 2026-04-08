import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import base64

# ================= CONFIG =================
st.set_page_config(page_title="UKS Digital", layout="wide")

BASE_DIR = os.path.dirname(__file__)
logo_uks = os.path.join(BASE_DIR, "logo_uks.png")
logo_sekolah = os.path.join(BASE_DIR, "logo_sekolah.png")
bg_login = os.path.join(BASE_DIR, "background.png")

# ================= SESSION PERSIST (ANTI LOGOUT) =================
if "auth" not in st.session_state:
    st.session_state.auth = False
if "role" not in st.session_state:
    st.session_state.role = ""

# ================= STYLE =================
def set_style(login=False):

    if os.path.exists(bg_login):
        with open(bg_login, "rb") as f:
            data = base64.b64encode(f.read()).decode()
    else:
        data = ""

    if login:
        container = """
        .block-container {
            max-width: 420px;
            margin: auto;
            margin-top: 80px;
            padding: 40px;
            border-radius: 25px;
            background: rgba(255,255,255,0.3);
            backdrop-filter: blur(25px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        """
    else:
        container = """
        .block-container {
            max-width: 100%;
            padding: 30px;
        }
        """

    st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{data}") no-repeat center center fixed;
        background-size: cover;
    }}

    {container}

    section[data-testid="stSidebar"] {{
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(15px);
    }}

    .card {{
        background: rgba(255,255,255,0.25);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}

    .stButton button {{
        width: 100%;
        border-radius: 25px;
        background: linear-gradient(90deg,#ff416c,#4facfe);
        color: white;
        font-weight: bold;
    }}

    input {{
        background: rgba(255,255,255,0.9) !important;
        color: black !important;
        border-radius: 10px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# ================= GSHEET =================
conn = st.connection("gsheets", type=GSheetsConnection)
URL = st.secrets["connections"]["gsheets"]["url"]

def load(sheet):
    try:
        return conn.read(spreadsheet=URL, worksheet=sheet, ttl=0)
    except:
        return pd.DataFrame()

def save(df, sheet):
    conn.update(spreadsheet=URL, worksheet=sheet, data=df)

# ================= USER =================
USERS = {
    "adminuks": {"password": "man1kotsiadmin", "role": "admin"},
    "useruks": {"password": "man1kotsiuser", "role": "user"}
}

# ================= LOGIN =================
if not st.session_state.auth:

    set_style(login=True)

    if os.path.exists(logo_uks):
        with open(logo_uks, "rb") as f:
            logo = base64.b64encode(f.read()).decode()
    else:
        logo = ""

    st.markdown(f"""
    <div style="text-align:center;">
        <img src="data:image/png;base64,{logo}" width="90">
        <h2>SISTEM UKS DIGITAL</h2>
        <p>MAN 1 KOTA SUKABUMI</p>
    </div>
    """, unsafe_allow_html=True)

    username = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    login = st.button("LOGIN")

    if login:
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.auth = True
            st.session_state.role = USERS[username]["role"]
            st.rerun()
        else:
            st.error("Login gagal")

# ================= MAIN =================
else:

    set_style(login=False)
    role = st.session_state.role

    # ===== SIDEBAR =====
    with st.sidebar:
        if os.path.exists(logo_sekolah):
            st.image(logo_sekolah, width=90)

        st.markdown("## 🏥 UKS DIGITAL")
        st.markdown(f"👤 **{role.upper()}**")

        menu = ["📊 Dashboard","📝 Input Pasien","🩺 Data Kesehatan"]

        if role == "admin":
            menu += ["💊 Stok Obat","📅 Kegiatan","📥 Kelola Data"]

        choice = st.radio("Menu", menu)

        if st.button("🚪 Logout"):
            st.session_state.clear()
            st.rerun()

    # ===== DASHBOARD =====
    if choice == "📊 Dashboard":

        st.title("📊 Dashboard")

        df = load("pasien")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pasien", len(df))
        col2.metric("Total Siswa", len(load("siswa")))
        col3.metric("Stok Obat", len(load("stok")))

    # ===== INPUT PASIEN =====
    elif choice == "📝 Input Pasien":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📝 Input Pasien")

        if st.session_state.get("notif_pasien"):
            st.success("✅ Data berhasil disimpan")
            st.session_state.notif_pasien = False

        df_s = load("siswa")
        df_p = load("pasien")

        tanggal = st.date_input("Tanggal")
        jam = st.time_input("Jam")

        kelas = st.selectbox("Kelas", sorted(df_s["kelas"].dropna().unique()))
        nama = st.selectbox("Nama", df_s[df_s["kelas"]==kelas]["nama_siswa"])

        keluhan = st.text_input("Keluhan")
        tindakan = st.text_input("Tindakan")

        if st.button("Simpan"):
            waktu = f"{tanggal} {jam}"
            new = pd.DataFrame([[waktu,nama,kelas,keluhan,tindakan]], columns=df_p.columns)
            df_p = pd.concat([df_p,new], ignore_index=True)
            save(df_p, "pasien")

            st.session_state.notif_pasien = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ===== DATA KESEHATAN =====
    elif choice == "🩺 Data Kesehatan":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🩺 Data Kesehatan")

        if st.session_state.get("notif_kesehatan"):
            st.success("✅ Data berhasil disimpan")
            st.session_state.notif_kesehatan = False

        df_k = load("kesehatan")
        df_s = load("siswa")

        tanggal = st.date_input("Tanggal")
        jam = st.time_input("Jam")

        kelas = st.selectbox("Kelas", sorted(df_s["kelas"].dropna().unique()))
        nama = st.selectbox("Nama", df_s[df_s["kelas"]==kelas]["nama_siswa"])

        bb = st.number_input("BB")
        tb = st.number_input("TB")
        tensi = st.text_input("Tensi")

        if st.button("Simpan"):
            waktu = f"{tanggal} {jam}"
            new = pd.DataFrame([[waktu,nama,kelas,bb,tb,tensi]], columns=df_k.columns)
            df_k = pd.concat([df_k,new], ignore_index=True)
            save(df_k, "kesehatan")

            st.session_state.notif_kesehatan = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ===== STOK OBAT =====
    elif choice == "💊 Stok Obat":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 💊 Stok Obat")

        df = load("stok")

        # Tambahan aman (tidak merubah struktur lama)
        if "Satuan" not in df.columns:
            df["Satuan"] = ""

        satuan_list = [
            "Box","Botol","Strip","Blister","Tube (salep)",
            "Vial/Ampul (injeksi)","Flabot (infus)",
            "Tablet","Kapsul","Kaplet","Sirup (ml)",
            "Drop","Suppositoria","Kaleng"
        ]

        nama = st.text_input("Nama Obat")
        jumlah = st.number_input("Jumlah")
        satuan = st.selectbox("Satuan", satuan_list)

        if st.button("Tambah"):
            waktu = pd.Timestamp.now()
            new = pd.DataFrame([[nama,jumlah,satuan,waktu]], columns=df.columns)
            df = pd.concat([df,new], ignore_index=True)
            save(df, "stok")
            st.success("Berhasil ditambahkan")
            st.rerun()

        st.markdown("### ✏️ Update Stok")
        if not df.empty:
            pilih = st.selectbox("Pilih Obat", df["Nama Obat"])
            jumlah_baru = st.number_input("Jumlah Baru")
            satuan_baru = st.selectbox("Satuan Baru", satuan_list)

            if st.button("Update"):
                df.loc[df["Nama Obat"]==pilih, "Jumlah"] = jumlah_baru
                df.loc[df["Nama Obat"]==pilih, "Satuan"] = satuan_baru
                save(df, "stok")
                st.success("Stok berhasil diupdate")
                st.rerun()

        st.dataframe(df)
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== KEGIATAN =====
    elif choice == "📅 Kegiatan":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📅 Kegiatan")

        df = load("kegiatan")

        tanggal = st.date_input("Tanggal")
        jam = st.time_input("Jam")

        kegiatan = st.text_input("Kegiatan")
        peserta = st.text_input("Peserta")
        ket = st.text_area("Keterangan")

        if st.button("Simpan"):
            waktu = f"{tanggal} {jam}"
            new = pd.DataFrame([[waktu,kegiatan,peserta,ket]], columns=df.columns)
            df = pd.concat([df,new], ignore_index=True)
            save(df, "kegiatan")

            st.success("Tersimpan")
            st.rerun()

        st.dataframe(df)
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== KELOLA =====
    elif choice == "📥 Kelola Data":

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📥 Kelola Data")

        tabel = st.selectbox("Pilih Tabel", ["siswa","pasien","kesehatan","stok","kegiatan"])
        df = load(tabel)

        st.dataframe(df)

    # ===== EDIT DATA =====
        st.markdown("### ✏️ Edit Data")

        if not df.empty:
            index = st.number_input("Pilih Index Baris", 0, len(df)-1, 0)

            row = df.iloc[index]
            updated = {}

            for col in df.columns:
                updated[col] = st.text_input(col, value=str(row[col]))

            if st.button("Simpan Perubahan"):
                for col in df.columns:
                    df.at[index, col] = updated[col]

                save(df, tabel)
                st.success("Data berhasil diupdate")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("---")
st.caption("© 2026 Sistem UKS Digital MAN 1 Kota Sukabumi")
