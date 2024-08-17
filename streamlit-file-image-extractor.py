import streamlit as st
import os
import io
import zipfile
from PIL import Image
import fitz  # PyMuPDF
import tempfile
import psutil

def get_drives():
    drives = []
    for partition in psutil.disk_partitions():
        if 'fixed' in partition.opts or 'cdrom' in partition.opts:
            drives.append(partition.device)
    return drives

def extract_images_from_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    image_count = 0
    extracted_images = []
    
    for page in pdf:
        for img in page.get_images(full=True):
            try:
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                
                image = Image.open(io.BytesIO(image_bytes))
                image_count += 1
                extracted_images.append((f"pdf_image_{image_count}.png", image_bytes))
            except Exception as e:
                st.warning(f"Could not extract an image: {str(e)}")
    
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

st.sidebar.markdown("<p class='title'>Upload the inspection report</p>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

# Get available drives and create a dropdown
drives = get_drives()
selected_drive = st.sidebar.selectbox("Select Drive", drives)

# Allow user to input additional path
additional_path = st.sidebar.text_input("Additional Path (optional)", "")

# Combine selected drive and additional path
save_path = os.path.join(selected_drive, additional_path.strip("/\\"))

st.markdown("<p class='title'>PDF Image Extractor</p>", unsafe_allow_html=True)

extract_button = st.button("Extract Corrosive Images")

if extract_button and uploaded_file is not None:
    try:
        with st.spinner("Extracting images..."):
            page_count, image_count, extracted_images = extract_images_from_pdf(uploaded_file)
            
            st.markdown(f"Processed PDF file: {uploaded_file.name}")
            st.markdown(f"Number of pages: {page_count}")
            st.markdown(f"Number of images extracted: {image_count}")
            
            if image_count > 0:
                st.success(f"Corrosion images extracted successfully {image_count}.")
                
                # Create a ZIP file in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                    for img_name, img_data in extracted_images:
                        zipf.writestr(img_name, img_data)
                
                # Provide download link for the ZIP file
                st.download_button(
                    label="Download Extracted Images",
                    data=zip_buffer.getvalue(),
                    file_name="extracted_images.zip",
                    mime="application/zip"
                )
                
                # Save images to selected location
                try:
                    os.makedirs(save_path, exist_ok=True)
                    for img_name, img_data in extracted_images:
                        with open(os.path.join(save_path, img_name), 'wb') as f:
                            f.write(img_data)
                    st.success(f"Images saved to: {save_path}")
                except Exception as e:
                    st.error(f"Failed to save images to selected location: {str(e)}")
            else:
                st.warning("No images were found in the uploaded file.")
                
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
elif extract_button and uploaded_file is None:
    st.warning("Please upload a PDF file before extracting images.")
else:
    st.markdown("Please upload a PDF file and click 'Extract Images' to begin.")
