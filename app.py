import streamlit as st
from supabase import create_client, Client
import datetime

# Konfigurasi Halaman agar rapi di HP & Laptop
st.set_page_config(page_title="Brain Dump 2026", page_icon="🧠", layout="wide")

# 1. Koneksi ke Supabase (Ganti dengan URL dan KEY milik Anda)
SUPABASE_URL = "sb_publishable_yb3ESAe1YYdZs6Y_xPfxsw_J88Xo5xk"
SUPABASE_KEY = "sb_secret_fY-YS7F8x_ZQhrY_D5yECA_U0pfPZXH"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

st.title("🧠 Brain Dump & Manajemen Harian 2026")
st.caption("Tumpahkan isi kepalamu di sini. Sinkronisasi otomatis antara HP dan Laptop.")

# --- FORM INPUT ---
with st.expander("➕ Tambah Brain Dump Baru", expanded=True):
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        aktivitas = st.text_input("Aktivitas / Catatan Detail")
        keterangan = st.text_area("Keterangan Tambahan (Opsional)", height=70)
        
    with col2:
        kategori = st.selectbox("Kategori", ["🍼 Urusan Anak (Zaldi)", "🏡 Orang Tua / Keluarga", "💻 Pekerjaan", "✨ Pribadi & Lainnya"])
        urgensi = st.selectbox("Tingkat Urgensi", ["Rendah", "Sedang", "Tinggi"])
        
    with col3:
        status = st.selectbox("Status", ["Belum Selesai", "Sedang Berjalan", "Selesai"])
        tanggal_selesai = st.date_input("Target Selesai", datetime.date.today())

    if st.button("Simpan ke Database", use_container_width=True):
        if aktivitas:
            data = {
                "kategori": kategori,
                "aktivitas": aktivitas,
                "urgensi": urgensi,
                "status": status,
                "tanggal_selesai": str(tanggal_selesai),
                "keterangan": keterangan
            }
            # Memasukkan data ke Supabase
            supabase.table("braindump").insert(data).execute()
            st.success("Berhasil disimpan secara realtime!")
            st.status("Memperbarui data...", expanded=False)
            st.rerun()
        else:
            st.error("Aktivitas tidak boleh kosong!")

# --- MENAMPILKAN DATA ---
st.subheader("📋 Daftar Fokus Anda")

# Mengambil data terbaru dari Supabase
response = supabase.table("braindump").select("*").order("created_at", desc=True).execute()
rows = response.data

if not rows:
    st.info("Belum ada data. Silakan tambah aktivitas di atas.")
else:
    # Memisahkan data per kategori agar sesuai dengan sistem Excel Anda
    kategori_pilihan = st.tabs(["🍼 Urusan Anak", "🏡 Keluarga", "💻 Pekerjaan", "✨ Semua"])
    
    def tampilkan_tabel(filter_kategori=None):
        for row in rows:
            if filter_kategori and filter_kategori not in row['kategori']:
                continue
            
            # Membuat visualisasi kartu (card layout) yang sangat nyaman dibaca di HP
            with st.container():
                c_urgensi = "🔴" if row['urgensi'] == "Tinggi" else ("🟡" if row['urgensi'] == "Sedang" else "🟢")
                st.markdown(f"### {c_urgensi} {row['aktivitas']}")
                st.markdown(f"**Kategori:** {row['kategori']} | **Status:** `{row['status']}` | **Target:** {row['tanggal_selesai']}")
                if row['keterangan']:
                    st.caption(f"Catatan: {row['keterangan']}")
                
                # Tombol Aksi Cepat untuk mengubah status
                col_a, col_b = st.columns([1, 6])
                with col_a:
                    if row['status'] != "Selesai":
                        if st.button("Selesai ✅", key=f"done_{row['id']}"):
                            supabase.table("braindump").update({"status": "Selesai"}).eq("id", row['id']).execute()
                            st.rerun()
                st.markdown("---")

    with kategori_pilihan[0]:
        tampilkan_tabel("Urusan Anak")
    with kategori_pilihan[1]:
        tampilkan_tabel("Orang Tua")
    with kategori_pilihan[2]:
        tampilkan_tabel("Pekerjaan")
    with kategori_pilihan[3]:
        tampilkan_tabel()
