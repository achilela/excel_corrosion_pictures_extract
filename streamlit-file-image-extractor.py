import streamlit as st
import os
import io
import zipfile
from PIL import Image
import fitz  # PyMuPDF

def extract_images_from_pdf(file, save_path):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    image_count = 0
    extracted_images = []
    
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                
                image = Image.open(io.BytesIO(image_bytes))
                image_count += 1
                image_filename = f"pdf_image_{image_count}.png"
                image_path = os.path.join(save_path, image_filename)
                image.save(image_path)
                extracted_images.append(image_path)
            except Exception as e:
                st.warning(f"Could not extract an image from PDF: {str(e)}")
                continue
    
    return len(pdf), image_count, extracted_images

st.set_page_config(page_title="PDF Image Extractor", layout="wide")

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

st.markdown("<p class='title'>PDF Image Extractor</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

extract_button = st.button("Extract Images")

if extract_button and uploaded_file is not None:
    try:
        with st.spinner("Extracting images..."):
            # Create a temporary directory to save images
            temp_dir = "temp_images"
            os.makedirs(temp_dir, exist_ok=True)
            
            page_count, image_count, extracted_images = extract_images_from_pdf(uploaded_file, temp_dir)
            
            st.markdown(f"Processed PDF file: {uploaded_file.name}")
            st.markdown(f"Number of pages: {page_count}")
            st.markdown(f"Number of images extracted: {image_count}")
            
            if image_count > 0:
                st.success(f"Successfully extracted {image_count} images.")
                
                # Create a ZIP file containing all extracted images
                zip_filename = "extracted_images.zip"
                with zipfile.ZipFile(zip_filename, 'w') as zipf:
                    for img_path in extracted_images:
                        zipf.write(img_path, os.path.basename(img_path))
                
                # Provide download link for the ZIP file
                with open(zip_filename, "rb") as f:
                    bytes_data = f.read()
                    st.download_button(
                        label="Download Extracted Images",
                        data=bytes_data,
                        file_name=zip_filename,
                        mime="application/zip"
                    )
            else:
                st.warning("No images were found in the uploaded file.")
            
            # Clean up: remove temporary files
            for img_path in extracted_images:
                os.remove(img_path)
            os.rmdir(temp_dir)
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
                
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
elif extract_button and uploaded_file is None:
    st.warning("Please upload a PDF file before extracting images.")
else:
    st.markdown("Please upload a PDF file and click 'Extract Images' to begin.")
