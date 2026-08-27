import streamlit as st
from pypdf import PdfReader, PdfWriter
from pdf2docx import Converter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
import io
import os

st.set_page_config(page_title="PDF Tool Suite", page_icon="📄", layout="wide")

st.title("📄 Multi-Tool PDF Manager")
st.caption("Solusi cepat untuk memanipulasi dokumen PDF mirip iLovePDF")

# Navigasi Menu
menu = st.sidebar.radio(
    "Pilih Fitur:",
    [
        "Merge PDF",
        "Split PDF",
        "Rotate PDF",
        "Protect PDF (Password)",
        "Add Watermark",
        "Compress PDF",
        "PDF to Word"
    ]
)

# Helper untuk membuat overlay watermark
def create_watermark(text, opacity=0.3, font_size=40):
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.setFont("Helvetica-Bold", font_size)
    can.setFillColor(Color(0.5, 0.5, 0.5, alpha=opacity))
    can.saveState()
    can.translate(300, 450)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    can.restoreState()
    can.save()
    packet.seek(0)
    return PdfReader(packet)

# ==================== 1. MERGE PDF ====================
if menu == "Merge PDF":
    st.header("🔗 Gabungkan PDF (Merge)")
    uploaded_files = st.file_uploader("Upload beberapa file PDF", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        st.write(f"Total file: **{len(uploaded_files)}**")
        if st.button("Gabungkan Semua File"):
            merger = PdfWriter()
            for pdf in uploaded_files:
                merger.append(pdf)
            
            output_stream = io.BytesIO()
            merger.write(output_stream)
            merger.close()
            output_stream.seek(0)
            
            st.success("File berhasil digabungkan!")
            st.download_button(
                label="⬇️ Download PDF Hasil Merge",
                data=output_stream,
                file_name="merged_document.pdf",
                mime="application/pdf"
            )

# ==================== 2. SPLIT PDF ====================
elif menu == "Split PDF":
    st.header("✂️ Pisahkan Halaman PDF (Split)")
    uploaded_file = st.file_uploader("Upload 1 file PDF", type="pdf", key="split")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        st.info(f"Total halaman dalam file: **{total_pages}**")
        
        page_range = st.text_input("Masukkan rentang halaman (contoh: 1-3 atau 2,4,5):", value=f"1-{total_pages}")
        
        if st.button("Ekstrak Halaman"):
            try:
                writer = PdfWriter()
                pages_to_extract = []
                
                for part in page_range.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        pages_to_extract.extend(range(start - 1, end))
                    else:
                        pages_to_extract.append(int(part) - 1)
                
                for idx in sorted(set(pages_to_extract)):
                    if 0 <= idx < total_pages:
                        writer.add_page(reader.pages[idx])
                
                output_stream = io.BytesIO()
                writer.write(output_stream)
                writer.close()
                output_stream.seek(0)
                
                st.success("Halaman berhasil diekstrak!")
                st.download_button(
                    label="⬇️ Download PDF Hasil Split",
                    data=output_stream,
                    file_name="split_document.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Format rentang halaman salah: {e}")

# ==================== 3. ROTATE PDF ====================
elif menu == "Rotate PDF":
    st.header("🔄 Putar Orientasi PDF")
    uploaded_file = st.file_uploader("Upload file PDF", type="pdf", key="rotate")
    
    if uploaded_file:
        rotation_angle = st.selectbox("Pilih sudut putar searah jarum jam:", [90, 180, 270])
        
        if st.button("Putar Dokumen"):
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            
            for page in reader.pages:
                page.rotate(rotation_angle)
                writer.add_page(page)
                
            output_stream = io.BytesIO()
            writer.write(output_stream)
            writer.close()
            output_stream.seek(0)
            
            st.success("Orientasi halaman berhasil diubah!")
            st.download_button(
                label="⬇️ Download PDF Baru",
                data=output_stream,
                file_name="rotated_document.pdf",
                mime="application/pdf"
            )

# ==================== 4. PROTECT PDF (PASSWORD) ====================
elif menu == "Protect PDF (Password)":
    st.header("🔒 Kunci PDF dengan Password")
    uploaded_file = st.file_uploader("Upload file PDF", type="pdf", key="protect")
    
    if uploaded_file:
        password = st.text_input("Masukkan Password Proteksi:", type="password")
        
        if st.button("Enkripsi Dokumen"):
            if not password:
                st.warning("Silakan isi password terlebih dahulu.")
            else:
                reader = PdfReader(uploaded_file)
                writer = PdfWriter()
                
                for page in reader.pages:
                    writer.add_page(page)
                
                # Enkripsi PDF menggunakan password
                writer.encrypt(user_password=password, algorithm="AES-256")
                
                output_stream = io.BytesIO()
                writer.write(output_stream)
                writer.close()
                output_stream.seek(0)
                
                st.success("Dokumen berhasil diproteksi dengan password!")
                st.download_button(
                    label="⬇️ Download PDF Terenkripsi",
                    data=output_stream,
                    file_name="protected_document.pdf",
                    mime="application/pdf"
                )

# ==================== 5. ADD WATERMARK ====================
elif menu == "Add Watermark":
    st.header("💧 Tambahkan Watermark Teks")
    uploaded_file = st.file_uploader("Upload file PDF", type="pdf", key="watermark")
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            watermark_text = st.text_input("Teks Watermark:", value="CONFIDENTIAL")
            font_size = st.slider("Ukuran Font:", min_value=20, max_value=80, value=40)
        with col2:
            opacity = st.slider("Transparansi (Opacity):", min_value=0.1, max_value=1.0, value=0.25, step=0.05)
            
        if st.button("Pasang Watermark"):
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            watermark_pdf = create_watermark(watermark_text, opacity, font_size)
            watermark_page = watermark_pdf.pages[0]
            
            for page in reader.pages:
                page.merge_page(watermark_page)
                writer.add_page(page)
                
            output_stream = io.BytesIO()
            writer.write(output_stream)
            writer.close()
            output_stream.seek(0)
            
            st.success("Watermark berhasil ditambahkan!")
            st.download_button(
                label="⬇️ Download PDF Ber-Watermark",
                data=output_stream,
                file_name="watermarked_document.pdf",
                mime="application/pdf"
            )

# ==================== 6. COMPRESS PDF ====================
elif menu == "Compress PDF":
    st.header("🗜️ Kompres Ukuran PDF")
    uploaded_file = st.file_uploader("Upload file PDF", type="pdf", key="compress")
    
    if uploaded_file:
        original_size = len(uploaded_file.getvalue()) / 1024
        st.write(f"Ukuran asli: **{original_size:.2f} KB**")
        
        if st.button("Kompres Dokumen"):
            reader = PdfReader(uploaded_file)
            writer = PdfWriter()
            
            for page in reader.pages:
                # Mengompres konten dan stream objek pada halaman
                page.compress_content_streams()
                writer.add_page(page)
            
            output_stream = io.BytesIO()
            writer.write(output_stream)
            writer.close()
            output_stream.seek(0)
            
            new_size = len(output_stream.getvalue()) / 1024
            st.success(f"Kompresi selesai! Ukuran baru: **{new_size:.2f} KB**")
            
            st.download_button(
                label="⬇️ Download PDF Terkompres",
                data=output_stream,
                file_name="compressed_document.pdf",
                mime="application/pdf"
            )

# ==================== 7. PDF TO WORD ====================
elif menu == "PDF to Word":
    st.header("📝 Konversi PDF ke Word (.docx)")
    uploaded_file = st.file_uploader("Upload file PDF", type="pdf", key="docx")
    
    if uploaded_file:
        if st.button("Konversi ke DOCX"):
            with st.spinner("Sedang mengonversi layout dan teks..."):
                temp_pdf_path = "temp_input.pdf"
                temp_docx_path = "temp_output.docx"
                
                with open(temp_pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                cv = Converter(temp_pdf_path)
                cv.convert(temp_docx_path, start=0, end=None)
                cv.close()
                
                with open(temp_docx_path, "rb") as f:
                    docx_data = f.read()
                
                if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)
                if os.path.exists(temp_docx_path): os.remove(temp_docx_path)
                
                st.success("Konversi selesai!")
                st.download_button(
                    label="⬇️ Download File Word (.docx)",
                    data=docx_data,
                    file_name="converted_document.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )