import json
import os
import unicodedata
import uuid
from multiprocessing import Pool, cpu_count


def ensure_output_dir(output_dir):
    os.makedirs(output_dir, exist_ok=True)


def load_json(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def remove_non_unicode_characters(text):
    return ''.join(c for c in text if unicodedata.category(c) not in ('Cn', 'Co', 'Cs') and ord(c) <= 0x10FFFF)


def remove_unusual_line_terminators(text):
    return text.replace('\u2028', '').replace('\u2029', '')


def combine_title_and_text(entry):
    if 'data' in entry:
        title = entry['data'].get('title', '')
        text = entry['data'].get('body', {}).get('Text', [])

        combined_text = title + ' ' + ' '.join(t.replace('\n', ' ') for t in text).strip()
        return combined_text
    else:
        print(f"'data' key not found in entry: {entry}")
        return ''


def extract_metadata(entry):
    if 'data' in entry:
        meta = entry['data'].get('meta_data', {})
        return {
            'URL': meta.get('URL', ''),
            'Author': meta.get('Author', ''),
            'Date': meta.get('Date', ''),
            'Tags': meta.get('Tags', [])
        }
    else:
        print(f"'data' key not found in entry: {entry}")
        return {'URL': '', 'Author': '', 'Date': '', 'Tags': []}


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def extract_data(input_file):
    combined_data_list = []
    metadata_list = []
    data = load_json(input_file)

    for entry in data.values():
        unique_id = str(uuid.uuid4())
        combined_text = combine_title_and_text(entry)
        if combined_text:
            combined_text = remove_unusual_line_terminators(combined_text)
            combined_text = remove_non_unicode_characters(combined_text)
            combined_data_list.append({
                'id': unique_id,
                'text': combined_text
            })
            metadata = extract_metadata(entry)
            metadata_list.append({
                'id': unique_id,
                'source': metadata['URL'],
                # 'authors': metadata['Author'],
                'date': metadata['Date'],
                'tags': metadata['Tags']
            })

    return combined_data_list, metadata_list


def process_file(input_file):
    print(f"Processing file: {input_file}")
    return extract_data(input_file)


def process_directory(input_dir, output_dir):
    ensure_output_dir(output_dir)
    input_files = []
    folder_count = 0
    json_file_count = 0

    for root, dirs, files in os.walk(input_dir):
        folder_count += len(dirs)
        for file in files:
            if file.endswith('.json'):
                input_files.append(os.path.join(root, file))
                json_file_count += 1

    print(f"Number of folders: {folder_count}")
    print(f"Number of JSON files found: {json_file_count}")

    combined_data_list = []
    metadata_list = []

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_file, input_files)

    for combined_data, metadata in results:
        combined_data_list.extend(combined_data)
        metadata_list.extend(metadata)

    save_json(combined_data_list, os.path.join(output_dir, 'texts.json'))
    save_json(metadata_list, os.path.join(output_dir, 'metadata.json'))

    print(f"Processed {json_file_count} JSON files.")


def main():
    input_dir = 'data/compile_all_data/news_data/news_articles'
    output_dir = 'data/compile_all_data/output_reformat_data'

    process_directory(input_dir, output_dir)


if __name__ == "__main__":
    main()
