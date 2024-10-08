import json
from collections import defaultdict


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def group_tags_by_id(metadata):
    tags_dict = defaultdict(list)
    for entry in metadata:
        tags_combination = tuple(sorted(entry['tags']))
        tags_dict[tags_combination].append(entry['id'])
    return tags_dict


def create_id_to_text_mapping(texts):
    return {entry['id']: entry['text'] for entry in texts}


def gather_text_by_tag(tags_dict, id_to_text):
    result = []
    for tags, ids in tags_dict.items():
        max_ids = ids[:10] if len(ids) > 10 else ids
        for unique_id in max_ids:
            if unique_id in id_to_text:
                result.append({
                    'tags': list(tags),
                    'text': id_to_text[unique_id]
                })
    return result


def save_to_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=4)


def main():
    metadata_path = 'data/compile_all_data/output_reformat_data/all_metadata.json'
    texts_path = 'data/compile_all_data/output_reformat_data/all_texts.json'
    metadata = load_json(metadata_path)
    texts = load_json(texts_path)

    tags_dict = group_tags_by_id(metadata)
    id_to_text = create_id_to_text_mapping(texts)
    result = gather_text_by_tag(tags_dict, id_to_text)

    output_data_path = 'data/compile_all_data/tag_sample_data/tag_10_sample.json'
    save_to_json(result, output_data_path)


if __name__ == '__main__':
    main()
