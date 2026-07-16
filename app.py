# --- MENAMPILKAN DATA ---
st.subheader("📋 Daftar Fokus Anda")

# Mengambil data dari Supabase dengan penanganan error yang aman
rows = []
try:
    # Menyederhanakan query untuk memastikan data bisa ditarik terlebih dahulu
    response = supabase.table("braindump").select("*").execute()
    rows = response.data
    
    # Melakukan pengurutan secara lokal di Python berdasarkan waktu dibuat (jika ada data)
    if rows and 'created_at' in rows[0]:
        rows = sorted(rows, key=lambda x: x['created_at'], reverse=True)
except Exception as e:
    st.error(f"Gagal memuat data dari database. Silakan periksa kembali tabel Supabase Anda.")
    st.caption(f"Detail kendala: {str(e)}")

if not rows:
    st.info("Belum ada data aktif. Silakan isi form di atas untuk menambahkan aktivitas baru.")
else:
    # Memisahkan data per kategori agar sesuai dengan sistem Excel Anda
    kategori_pilihan = st.tabs(["🍼 Urusan Anak", "🏡 Keluarga", "💻 Pekerjaan", "✨ Semua"])
    
    def tampilkan_tabel(filter_kategori=None):
        data_ditemukan = False
        for row in rows:
            # Mengantisipasi jika ada kolom yang bernilai None/Kosong
            kat = row.get('kategori', '')
            if filter_kategori and filter_kategori not in kat:
                continue
            
            data_ditemukan = True
            # Membuat visualisasi kartu (card layout) yang nyaman dibaca di HP
            with st.container():
                urgensi_val = row.get('urgensi', 'Rendah')
                c_urgensi = "🔴" if urgensi_val == "Tinggi" else ("🟡" if urgensi_val == "Sedang" else "🟢")
                
                st.markdown(f"### {c_urgensi} {row.get('aktivitas', 'Tanpa Nama')}")
                st.markdown(f"**Kategori:** {kat} | **Status:** `{row.get('status', 'Belum Selesai')}` | **Target:** {row.get('tanggal_selesai', '-')}")
                
                if row.get('keterangan'):
                    st.caption(f"Catatan: {row['keterangan']}")
                
                # Tombol Aksi Cepat untuk mengubah status
                if row.get('status') != "Selesai":
                    if st.button("Selesai ✅", key=f"done_{row.get('id')}"):
                        try:
                            supabase.table("braindump").update({"status": "Selesai"}).eq("id", row['id']).execute()
                            st.rerun()
                        except Exception as up_err:
                            st.error("Gagal memperbarui status.")
                st.markdown("---")
        
        if not data_ditemukan:
            st.caption("Tidak ada aktivitas di kategori ini.")

    with kategori_pilihan[0]:
        tampilkan_tabel("Urusan Anak")
    with kategori_pilihan[1]:
        tampilkan_tabel("Orang Tua")
    with kategori_pilihan[2]:
        tampilkan_tabel("Pekerjaan")
    with kategori_pilihan[3]:
        tampilkan_tabel()
