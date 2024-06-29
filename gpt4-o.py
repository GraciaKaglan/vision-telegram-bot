from openai import OpenAI
import dotenv
import base64
import json
import os 
import logging

from telegram import(
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup)
from telegram.ext import( 
    ApplicationBuilder, 
    CommandHandler,
    MessageHandler, 
    filters, 
    ContextTypes,
    CallbackQueryHandler)

dotenv.load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


prompt = """Extract information from package labels in the image and 
return as a JSON object with this exact structure:
{
    "product_name": {"value": "<value>", "accuracy": <value>},
    "lot_number": {"value": "<value>", "accuracy": <value>},
    "quantity": {"value": "<value>", "accuracy": <value>},
    "expiry_date": {"value": "<value>", "accuracy": <value>},
    "gtin_14": {"value": "<value>", "accuracy": <value>},
    "complete_barcode": {"value": "<value>", "accuracy": <value>}
}
Include product name and expiry date as the most important. Provide accuracy for each entity.
"""


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

    # Create inline keyboard with a button to modify the response
    keyboard = [
        [InlineKeyboardButton("Modify Response", callback_data='modify_response')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the response back to the user with the button
    await update.message.reply_text(response_text, reply_markup=reply_markup)


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
    product_name = response_data["product_name"]['value']
    expiry_date = response_data["expiry_date"]['value']

    return f"Product Name: {product_name}\nExpiry Date: {expiry_date}"

async def modify_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Send a message to the user to enter the corrected response
    await query.edit_message_text(
        text="Please enter the corrected response in the following format:\nProduct Name: nom du produit \nExpiry Date: dd/mm/yy"
    )

    # Set up a handler to capture the user's corrected response
    context.user_data['awaiting_correction'] = True

async def receive_correction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('awaiting_correction'):
        corrected_response = update.message.text
        await update.message.reply_text(f"Received corrected response:\n{corrected_response}")
        context.user_data['awaiting_correction'] = False

def main() -> None:
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(os.environ.get("TG_TOKEN")).build()

    # Add command handler for the start command
    application.add_handler(CommandHandler("start", start))

    # Add handler for receiving images
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))

    # Add handler for callback queries (button presses)
    application.add_handler(CallbackQueryHandler(modify_response, pattern='modify_response'))

    # Add handler for receiving corrected response
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), receive_correction))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
