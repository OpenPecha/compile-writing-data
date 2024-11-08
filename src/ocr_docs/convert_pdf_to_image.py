import os
from pdf2image import convert_from_path

# Function to convert PDF to images and maintain folder structure
def convert_pdfs_to_images(pdf_dir, output_dir, dpi=300):
    # Walk through the directory structure
    for root, dirs, files in os.walk(pdf_dir):
        for pdf_file in files:
            if pdf_file.endswith(".pdf"):
                pdf_path = os.path.join(root, pdf_file)
                
                # Create a subdirectory for each PDF, named after the PDF without the extension
                pdf_name = os.path.splitext(pdf_file)[0]
                pdf_output_dir = os.path.join(output_dir, os.path.relpath(root, pdf_dir), pdf_name)
                
                # Create output directory if it doesn't exist
                if not os.path.exists(pdf_output_dir):
                    os.makedirs(pdf_output_dir)
                
                print(f"Converting {pdf_file}...")
                
                # Convert each page of the PDF to image
                pages = convert_from_path(pdf_path, dpi=dpi)
                
                # Save each page as an image in the PDF's subdirectory
                for i, page in enumerate(pages):
                    output_path = os.path.join(pdf_output_dir, f"{pdf_name}_page_{i + 1}.png")
                    page.save(output_path, 'PNG')
                    print(f"Saved {output_path}")

# Define input and output directories
pdf_directory = 'data/text_book/text_books'
output_directory = 'data/text_book/page_images/maths_8_class'

# Convert PDFs to images
convert_pdfs_to_images(pdf_directory, output_directory)
