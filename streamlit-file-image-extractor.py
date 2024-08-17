import streamlit as st
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import openpyxl
from openpyxl.drawing.image import Image as XLImage

def extract_images_from_excel(file, save_path):
    workbook = openpyxl.load_workbook(file)
    image_count = 0
    sheet_count = len(workbook.sheetnames)
    
    for sheet in workbook:
        for image in sheet._images:
            image_count += 1
            if hasattr(image, 'ref'):  # For embedded images
                if hasattr(image.ref, 'image'):
                    img = Image.open(io.BytesIO(image.ref.image.content()))
                elif hasattr(image.ref, 'blipFill'):
                    blob = image.ref.blipFill.blip.embed
                    img = Image.open(io.BytesIO(workbook._archive.read(blob)))
            elif hasattr(image, '_data'):  # For images stored directly
                img = Image.open(io.BytesIO(image._data()))
            else:
                continue  # Skip if we can't process this image
            
            img.save(os.path.join(save_path, f"excel_image_{image_count}.png"))
    
    return sheet_count, image_count

def extract_images_from_pdf(file, save_path):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
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
            image.save(os.path.join(save_path, f"pdf_image_{image_count}.png"))
    
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

# Dropdown for selecting save path
save_paths = ["Desktop", "Documents", "Downloads"]
selected_path = st.selectbox("Select save location", save_paths)

# Map selected path to actual directory
path_mapping = {
    "Desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
    "Documents": os.path.join(os.path.expanduser("~"), "Documents"),
    "Downloads": os.path.join(os.path.expanduser("~"), "Downloads")
}

save_path = path_mapping[selected_path]

# Extract button
extract_button = st.button("Extract Images")

if extract_button and uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    extracted_folder = os.path.join(save_path, "extracted_images")
    if not os.path.exists(extracted_folder):
        os.makedirs(extracted_folder)
    
    try:
        if file_extension in [".xlsx", ".xls"]:
            sheet_count, image_count = extract_images_from_excel(uploaded_file, extracted_folder)
            st.markdown(f"Processed Excel file: {uploaded_file.name}")
            st.markdown(f"Number of sheets: {sheet_count}")
            st.markdown(f"Number of images extracted: {image_count}")
        elif file_extension == ".pdf":
            page_count, image_count = extract_images_from_pdf(uploaded_file, extracted_folder)
            st.markdown(f"Processed PDF file: {uploaded_file.name}")
            st.markdown(f"Number of pages: {page_count}")
            st.markdown(f"Number of images extracted: {image_count}")
        else:
            st.error("Unsupported file format. Please upload an Excel or PDF file.")
        
        if image_count > 0:
            st.success(f"Images have been extracted and saved to: {extracted_folder}")
        else:
            st.warning("No images were found in the uploaded file.")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
elif extract_button and uploaded_file is None:
    st.warning("Please upload a file before extracting images.")
else:
    st.markdown("Please upload an Excel or PDF file and click 'Extract Images' to begin.")
