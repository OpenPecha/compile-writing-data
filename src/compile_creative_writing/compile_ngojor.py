from utils import process_directory, save_to_json, extract_tibetan_text_yigdrel


def main():
    directory_path = 'data/txt/ngojor'
    output_file = 'data/compiled_json/drc_ngojor.json'
    data = process_directory(directory_path, extract_tibetan_text_yigdrel)
    save_to_json(data, output_file)
    print(f"Extraction complete. Data saved to {output_file}.")
    
if __name__ == "__main__":
    main()
    