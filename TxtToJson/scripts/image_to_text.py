import os
import random
import string
from google.cloud import vision

# Initialize Vision API Client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/workspaces/vision-telegram-bot/credentials/client_file_vision-telegram-bot.json"
client = vision.ImageAnnotatorClient()

def generate_random_filename(extension=".txt"):
    """Generate a random filename to avoid overwriting."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + extension

def extract_text_from_image(image_path):
    """Extract text from an image using Google Vision API."""
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'Google Vision API Error: {response.error.message}')

    return texts[0].description if texts else ""

def process_images(input_folder, output_folder):
    """Process all images in a folder and save extracted text to random files."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            text = extract_text_from_image(image_path)

            output_file = os.path.join(output_folder, generate_random_filename())
            with open(output_file, 'w') as file:
                file.write(text)
            print(f"Extracted text saved to: {output_file}")

if __name__ == "__main__":
    input_folder = "TxtToJson/test_images"
    output_folder = "TxtToJson/Txt"
    process_images(input_folder, output_folder)
