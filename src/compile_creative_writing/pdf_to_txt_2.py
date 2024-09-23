import fitz  # PyMuPDF

def extract_text_from_identity_h_pdf(pdf_path, txt_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Open a text file to write the extracted text
    with open(txt_path, 'w', encoding='utf-8') as text_file:
        # Iterate through each page in the PDF
        for page_num in range(len(pdf_document)):
            # Get the page
            page = pdf_document.load_page(page_num)
            
            # Try extracting the text in different formats
            # "text" is standard, "textpage" retrieves recognized characters, 
            # and "rawdict" gets raw layout information
            text = page.get_text("text")  # Try "textpage" or "rawdict" if this doesn't work
            
            # Write the text to the file
            text_file.write(text)
            text_file.write('\n')  # Add a newline after each page

    # Close the PDF document
    pdf_document.close()
    print(f"Text has been extracted and saved to {txt_path}")

# Example usage
pdf_path = 'data/DRC/Dhomgyun Monlam unifont Final.pdf'  # Update with your PDF file path
txt_path = 'data//Dhomgyun Monlam unifont Final.txt'   # Update with your desired output text file path
extract_text_from_identity_h_pdf(pdf_path, txt_path)
