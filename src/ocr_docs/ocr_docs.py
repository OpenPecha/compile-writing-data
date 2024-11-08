import os
import io
import json
import logging
import gzip
from pathlib import Path
from google.cloud import vision
from google.cloud.vision import AnnotateImageResponse

vision_client = vision.ImageAnnotatorClient()

def check_google_credentials():
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        raise EnvironmentError("Set the GOOGLE_APPLICATION_CREDENTIALS environment variable.")

def load_image(image_path):
    with io.open(image_path, "rb") as image_file:
        return image_file.read()

def perform_ocr(image_content, lang_hint=None):
    ocr_image = vision.Image(content=image_content)
    features = [{"type_": vision.Feature.Type.DOCUMENT_TEXT_DETECTION, "model": "builtin/weekly"}]
    image_context = {"language_hints": [lang_hint]} if lang_hint else {}
    
    response = vision_client.annotate_image({
        "image": ocr_image,
        "features": features,
        "image_context": image_context,
    })

    response_json = AnnotateImageResponse.to_json(response)
    return json.loads(response_json)

def gzip_string(string_):
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="w") as fo:
        fo.write(string_.encode())
    return out.getvalue()

def save_results(result, json_path, txt_path):
    result_json = json.dumps(result)
    gzip_result = gzip_string(result_json)
    json_path.write_bytes(gzip_result)

    full_text = result.get("fullTextAnnotation", {}).get("text", "")
    if full_text:
        formatted_text = organize_text_by_bounding_boxes(result)
        txt_path.write_text(formatted_text, encoding="utf-8")
        print(f"OCR completed and saved as: {json_path} and {txt_path}.")
    else:
        logging.warning(f"No text detected for the image.")

def organize_text_by_bounding_boxes(result):
    if "textAnnotations" not in result:
        return ""

    blocks = sorted(result['textAnnotations'], key=lambda b: b['boundingPoly']['vertices'][0]['y'])
    structured_text = ""
    last_y = 0

    for block in blocks:
        vertices = block['boundingPoly']['vertices']
        top_left_y = vertices[0]['y']

        if top_left_y - last_y > 10:  # Adjust gap threshold based on needs
            structured_text += "\n"

        structured_text += block['description'] + " "
        last_y = top_left_y

    return structured_text

def process_image(image_path, OCR_json_root, OCR_txt_root, images_dir, lang=None):
    relative_path = image_path.relative_to(images_dir)
    json_output_path = OCR_json_root / relative_path.with_suffix('.json.gz')
    txt_output_path = OCR_txt_root / relative_path.with_suffix('.txt')
    json_output_path.parent.mkdir(parents=True, exist_ok=True)
    txt_output_path.parent.mkdir(parents=True, exist_ok=True)

    if json_output_path.is_file() and txt_output_path.is_file():
        print(f"Skipping already processed image: {relative_path}")
        return

    try:
        image_content = load_image(image_path)
        result = perform_ocr(image_content, lang)
        save_results(result, json_output_path, txt_output_path)
    except Exception as e:
        logging.exception(f"Error processing {image_path}: {e}")

def process_images_in_directory(images_dir, OCR_json_root, OCR_txt_root):
    for sub_dir in images_dir.rglob("*"):
        if sub_dir.is_file() and sub_dir.suffix.lower() in {".png", ".tiff", ".tif", ".jpg", ".jpeg"}:
            lang = sub_dir.suffix.lower()[1:]
            process_image(sub_dir, OCR_json_root, OCR_txt_root, images_dir, lang)
        elif sub_dir.is_dir():
            continue
        else:
            logging.warning(f"Unsupported file or directory: {sub_dir.name}")

def main():
    check_google_credentials()
    input_images_dir = Path("data/text_book/page_images/Math-8-Textbook")
    OCR_json_root = Path("data/text_book/page_images/ocr_json")
    OCR_txt_root = Path("data/text_book/page_images/ocr_text")

    OCR_json_root.mkdir(parents=True, exist_ok=True)
    OCR_txt_root.mkdir(parents=True, exist_ok=True)

    process_images_in_directory(input_images_dir, OCR_json_root, OCR_txt_root)

if __name__ == "__main__":
    main()
