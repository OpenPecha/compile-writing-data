import json
import os
import unicodedata


def ensure_output_dir(output_dir):
    os.makedirs(output_dir, exist_ok=True)


def load_json(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def remove_ambiguous_characters(text):
    return ''.join(c for c in text if not unicodedata.category(c).startswith('C'))


def combine_title_and_text(entry):
    title = remove_ambiguous_characters(entry['data']['title'])
    text = entry['data']['body']['Text']
    combined_text = remove_ambiguous_characters(title) + '\n' + ' '.join(
        remove_ambiguous_characters(t) for t in text).replace('\n', ' ').strip()
    return combined_text


def extract_metadata(entry):
    meta = entry['data']['meta_data']
    return {
        'URL': meta['URL'],
        'Author': meta['Author'],
        'Date': meta['Date'],
        'Tags': meta['Tags']
    }


def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def extract_data(input_file, output_dir):
    ensure_output_dir(output_dir)
    data = load_json(input_file)

    combined_data = {}
    metadata = {}

    for unique_id, entry in data.items():
        combined_data[unique_id] = {'text': combine_title_and_text(entry)}
        metadata[unique_id] = extract_metadata(entry)

    save_json(combined_data, os.path.join(output_dir, 'texts.json'))
    save_json(metadata, os.path.join(output_dir, 'metadata.json'))

    print(f"Data extracted and saved to {output_dir}")


input_file = 'data/compile_all_data/news_data/News Article/Bangchen/Bangchen_ALL_content_ཆེད་བརྗོད།.json'
output_dir = 'data/compile_all_data/output_reformat_data'

extract_data(input_file, output_dir)
