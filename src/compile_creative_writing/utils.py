import re
import json
import os

# for saldak format


def extract_tibetan_text_saldak(lines, filename):
    title_regex = r'^(.*?)༄༅།'
    json_data = []
    current_title = None
    current_text = []

    base_filename = os.path.splitext(filename)[0]  # Remove extension
    type_value = base_filename.split('_')[1] if '_' in base_filename else "unknown"

    for i, line in enumerate(lines):
        if not re.search(r'[\u0F00-\u0FFF]', line):
            continue

        title_match = re.search(title_regex, line)
        if title_match:
            if current_title is not None:
                json_data.append({
                    'data': {
                        'title': current_title,
                        'text': ' '.join(current_text).strip()
                    },
                    'meta_data': {
                        'type': type_value
                    }
                })
            current_title = lines[i - 1].strip() if i > 0 else "Untitled"
            current_text = []

        if '༄༅།' in line:
            start_index = line.index('༄༅།')
            current_text.append(line[start_index:].strip())
        elif current_title is not None:
            current_text.append(line.strip())

    if current_title is not None:
        json_data.append({
            'data': {
                'title': current_title,
                'text': ' '.join(current_text).strip()
            },
            'meta_data': {
                'type': type_value
            }
        })

    return json_data

# for yigdrel format


def extract_tibetan_text_yigdrel(lines, filename):
    """Extract Tibetan text from saldak and include metadata."""
    json_data = []
    current_title = None
    current_text = []
    base_filename = os.path.splitext(filename)[0]
    type_value = base_filename.split('_')[1] if '_' in base_filename else "unknown"

    for i, line in enumerate(lines):
        if not re.search(r'[\u0F00-\u0FFF]', line):
            continue

        if '༄༅།' in line:
            if current_title is not None:
                json_data.append({
                    'data': {
                        'heading': current_title,
                        'text': ' '.join(current_text).strip()
                    },
                    'meta_data': {
                        'type': type_value
                    }
                })
            current_title = line.strip()
            current_text = []
            continue

        if current_title is not None:
            current_text.append(line.replace('\t', '').strip())

    if current_title is not None:
        json_data.append({
            'data': {
                'heading': current_title,
                'text': ' '.join(current_text).strip()
            },
            'meta_data': {
                'type': type_value
            }
        })

    return json_data


def process_file(file_path, extract_function):
    """Process a single text file to extract Tibetan text using the provided extraction function."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    filename = os.path.basename(file_path)
    return extract_function(lines, filename)


def process_directory(directory, extract_function):
    """Process all text files in the specified directory using the provided extraction function."""
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            file_data = process_file(file_path, extract_function)
            all_data.extend(file_data)
    return all_data


def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
