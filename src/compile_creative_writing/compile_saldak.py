from utils import process_directory, save_to_json, extract_tibetan_text_saldak


def main():
    directory_path = 'data/txt/saldak'
    output_file = 'data/compiled_json/drc_saldak.json'
    data = process_directory(directory_path, extract_tibetan_text_saldak)
    save_to_json(data, output_file)
    print(f"Extraction complete. Data saved to {output_file}.")

if __name__ == "__main__":
    main()
