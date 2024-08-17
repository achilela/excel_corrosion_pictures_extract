import streamlit as st
import io
import zipfile
from PIL import Image
import fitz  # PyMuPDF

def convert_to_png(image_bytes):
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if the image is in CMYK or other modes
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = io.BytesIO()
            img.save(output, format='PNG')
            return output.getvalue()
    except Exception as e:
        st.warning(f"Could not convert image to PNG: {str(e)}")
        return None

def extract_images_from_pdf(file, start_index):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    image_count = 0
    extracted_images = []
    
    for page in pdf:
        for img in page.get_images(full=True):
            try:
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                
                png_bytes = convert_to_png(image_bytes)
                if png_bytes:
                    image_count += 1
                    file_name = f"corrosion.{start_index + image_count}.png"
                    extracted_images.append((file_name, png_bytes))
            except Exception as e:
                st.warning(f"Could not extract an image from {file.name}: {str(e)}")
    
    return len(pdf), image_count, extracted_images

st.set_page_config(page_title="Multi-PDF Image Extractor (PNG)", layout="wide")

st.markdown("""
<style>
    body {
        font-family: 'Tw Cen MT', sans-serif;
    }
    .title {
        font-size: 14px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("<p class='title'>Upload PDFs</p>", unsafe_allow_html=True)
uploaded_files = st.sidebar.file_uploader("Choose up to 5 PDF files", type=["pdf"], accept_multiple_files=True)

st.markdown("<p class='title'>Multi-PDF Image Extractor (PNG)</p>", unsafe_allow_html=True)

extract_button = st.button("Extract Images")

if extract_button and uploaded_files:
    if len(uploaded_files) > 5:
        st.warning("You can only process up to 5 PDF files at a time. Please reduce the number of selected files.")
    else:
        try:
            all_extracted_images = []
            total_page_count = 0
            total_image_count = 0
            current_index = 0

            with st.spinner("Extracting and converting images to PNG..."):
                for uploaded_file in uploaded_files:
                    page_count, image_count, extracted_images = extract_images_from_pdf(uploaded_file, current_index)
                    all_extracted_images.extend(extracted_images)
                    total_page_count += page_count
                    total_image_count += image_count
                    current_index += image_count
                    
                    st.markdown(f"Processed PDF file: {uploaded_file.name}")
                    st.markdown(f"Number of pages: {page_count}")
                    st.markdown(f"Number of images extracted: {image_count}")
                    st.markdown("---")
                
                st.markdown(f"**Total pages processed: {total_page_count}**")
                st.markdown(f"**Total images extracted and converted to PNG: {total_image_count}**")
                
                if total_image_count > 0:
                    st.success(f"Successfully extracted and converted {total_image_count} images from {len(uploaded_files)} PDF(s).")
                    
                    # Create a ZIP file in memory
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                        for img_name, img_data in all_extracted_images:
                            zipf.writestr(img_name, img_data)
                    
                    # Provide download link for the ZIP file
                    st.download_button(
                        label="Download All Extracted PNG Images",
                        data=zip_buffer.getvalue(),
                        file_name="extracted_png_images.zip",
                        mime="application/zip"
                    )
                else:
                    st.warning("No images were found in the uploaded PDF file(s).")
                    
        except Exception as e:
            st.error(f"An error occurred while processing the file(s): {str(e)}")
elif extract_button and not uploaded_files:
    st.warning("Please upload at least one PDF file before extracting images.")
else:
    st.markdown("Please upload up to 5 PDF files and click 'Extract Images' to begin.")
