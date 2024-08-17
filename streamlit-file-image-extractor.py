import streamlit as st
import pandas as pd
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import openpyxl
from openpyxl.drawing.image import Image as XLImage

def extract_images_from_excel(file):
    workbook = openpyxl.load_workbook(file)
    image_count = 0
    sheet_count = len(workbook.sheetnames)
    
    for sheet in workbook:
        for image in sheet._images:
            image_count += 1
            img = XLImage(io.BytesIO(image._data()))
            img.save(f"extracted_images/excel_image_{image_count}.png")
    
    return sheet_count, image_count

def extract_images_from_pdf(file):
    pdf = fitz.open(file)
    image_count = 0
    
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        images = page.get_images()
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            
            image = Image.open(io.BytesIO(image_bytes))
            image_count += 1
            image.save(f"extracted_images/pdf_image_{image_count}.png")
    
    return len(pdf), image_count

st.set_page_config(page_title="File Image Extractor", layout="wide")

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

st.markdown("<p class='title'>File Image Extractor</p>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='title'>Upload File</p>", unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("Choose an Excel or PDF file", type=["xlsx", "xls", "pdf"])

if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if not os.path.exists("extracted_images"):
        os.makedirs("extracted_images")
    
    if file_extension in [".xlsx", ".xls"]:
        sheet_count, image_count = extract_images_from_excel(uploaded_file)
        st.markdown(f"Processed Excel file: {uploaded_file.name}")
        st.markdown(f"Number of sheets: {sheet_count}")
        st.markdown(f"Number of images extracted: {image_count}")
    elif file_extension == ".pdf":
        page_count, image_count = extract_images_from_pdf(uploaded_file)
        st.markdown(f"Processed PDF file: {uploaded_file.name}")
        st.markdown(f"Number of pages: {page_count}")
        st.markdown(f"Number of images extracted: {image_count}")
    else:
        st.error("Unsupported file format. Please upload an Excel or PDF file.")
    
    if image_count > 0:
        st.success(f"Images have been extracted and saved to the 'extracted_images' folder.")
    else:
        st.warning("No images were found in the uploaded file.")
else:
    st.markdown("Please upload an Excel or PDF file to begin.")
