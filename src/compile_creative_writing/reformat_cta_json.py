import os
import json
import uuid

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_text_data(content, unique_id):
    heading = content['data'].get('heading', '')
    text = content['data'].get('text', '')
    combined_text = f"{heading} {text}".strip()
    return {
        "id": unique_id,
        "text": combined_text
    }

def extract_metadata(content, filename, unique_id):
    type_value = content['meta_data']['type']
    stripped_filename = filename.split('_')[0].strip().split('.')[0]
    return {
        "id": unique_id,
        "source": stripped_filename,
        "date": "",
        "tags": [type_value, stripped_filename],
    }

def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def process_json_files(input_dir, output_dir):
    text_data = []
    metadata_data = []

    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            contents = load_json_file(file_path)

            if isinstance(contents, list):
                for content in contents:
                    unique_id = str(uuid.uuid4())  # Generate a unique ID for each entry
                    text_data.append(extract_text_data(content, unique_id))
                    metadata_data.append(extract_metadata(content, filename, unique_id))
            else:
                print(f"Expected a list in file {filename}, but found: {type(contents)}")

    save_to_json(text_data, os.path.join(output_dir, 'cta_text.json'))
    save_to_json(metadata_data, os.path.join(output_dir, 'cta_metadata.json'))

if __name__ == "__main__":
    input_directory = "data/compile_cta_data/compiled_json"
    output_directory = "data/compile_cta_data/reformatted_output"
    process_json_files(input_directory, output_directory)
