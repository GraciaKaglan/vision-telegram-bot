from openai import OpenAI
import dotenv
import base64
import json
import os 
import logging

from telegram import Update
from telegram.ext import( 
    ApplicationBuilder, 
    CommandHandler,
    MessageHandler, 
    filters, 
    ContextTypes)

dotenv.load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


prompt = """You are a document extraction tool designed to process
          package labels from images. Your task is to identify and
          extract relevant information from each label detected in
          the image and return this data as a JSON object.
          The object should adhere to the agreed structure,
          capturing details such as product name, Lot Number,
          expiry date, quantity, gtin_14, complete barcode and
          additional details. The product name and expiry date are
          the most important informations.
          Additionally, include an accuracy
          value ranging from 0 to 1 for each extracted entity,
          reflecting the confidence in the extraction's
          correctness. Use the Exact following JSON format:
{
  "labels": [
    {
      "product_name": {"value": "<extracted value>", "accuracy": <accuracy value>},
      "number_of_labels": {"value": <extracted value>, "accuracy": <accuracy value>},
      "quantity": {"value": <extracted value>, "accuracy": <accuracy value>},
      "expiry_date": {"value": "<extracted value>", "accuracy": <accuracy value>},
      "barcodes": {
        "gtin_14": {"value": "<extracted value>", "accuracy": <accuracy value>},
        "complete_barcode": {"value": "<extracted value>", "accuracy": <accuracy value>}
      }
    }
  ]
}"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Send me an image, and I will process it for you.')

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Get the file id of the image
    file_id = update.message.photo[-1].file_id
    new_file = await context.bot.get_file(file_id)

    # Download the image
    file_path = os.path.join('downloads', f'{file_id}.jpg')
    os.makedirs('downloads', exist_ok=True)
    await new_file.download_to_drive(file_path)

    # Process the image with GPT-4 (this example assumes OCR or some image-to-text processing)
    response_text = process_image_with_gpt4(file_path)

    # Send the response back to the user
    await update.message.reply_text(response_text)


def process_image_with_gpt4(file_path: str) -> str:
    # Process the image with GPT4-o

    with open(file_path, 'rb') as image_file:
        image_content = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_content}"
                        }
                    }
                ]
            },
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0.1,
        presence_penalty=0.1,
    )

    response_message_content = response.choices[0].message.content
    response_data = json.loads(response_message_content)
    print(response_data)
    product_name = response_data['labels'][0]["product_name"]['value']
    expiry_date = response_data['labels'][0]["expiry_date"]['value']

    return f"Product Name: {product_name}\nExpiry Date: {expiry_date}"

def main() -> None:
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(os.environ.get("TG_TOKEN")).build()

    # Add command handler for the start command
    application.add_handler(CommandHandler("start", start))

    # Add handler for receiving images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
