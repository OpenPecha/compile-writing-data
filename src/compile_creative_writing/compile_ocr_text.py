import os
import json

def extract_text_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        heading_start = content.find('༄༅།')
        if heading_start != -1:
            heading_end = content.find('\n', heading_start)
            heading = content[heading_start:heading_end]  # Preserve the heading as is
            text = content[heading_end:]  # Get the rest of the text
            # Remove unwanted newline and tab characters
            text = text.replace('\n', ' ').replace('\t', ' ').strip()  # Replace with space or adjust as needed
        else:
            heading = ''
            text = content.replace('\n', ' ').replace('\t', ' ').strip()  # Remove unwanted characters
        return heading, text

def compile_txt_to_json(input_dir, output_json):
    compiled_data = []
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                heading, text = extract_text_from_file(file_path)
                
                compiled_data.append({
                    'data': {
                        'heading': heading,
                        'text': text
                    },
                    'meta_data': {
                        'type': "ཡིག་སྒྲེལ་"
                    }
                })
    
    with open(output_json, 'w', encoding='utf-8') as json_file:
        json.dump(compiled_data, json_file, ensure_ascii=False, indent=4)

# Usage
input_directory = 'data/compile_cta_data/cleaned_ocr_txt/DOH'
output_json_file = 'data/compile_cta_data/ocr_compiled_data/ནང་སྲིད་ལས་ཁུངས་_yigdrelOCR.json'
compile_txt_to_json(input_directory, output_json_file)
