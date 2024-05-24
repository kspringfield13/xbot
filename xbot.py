import tweepy, httpx, asyncio, logging, json, random, requests, tempfile, os, re, csv, time, openai, datetime, argparse, pandas as pd
from requests_oauthlib import OAuth1, OAuth1Session
from dotenv import load_dotenv
from datetime import timedelta
from PIL import Image
from prettytable import PrettyTable

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv('.env')

# Argument parsing
# "python xbot.py test" for testing
parser = argparse.ArgumentParser(description="X Bot")
parser.add_argument('mode', choices=['test', 'run'], help="Mode to run the bot in: 'test' or 'run'")
args = parser.parse_args()

# Configuration
TESTING_MODE = (args.mode == 'test')
ENABLE_POST_TO_X = not TESTING_MODE
ENABLE_POST_TO_DISCORD = not TESTING_MODE
# Number of Posts
NUMBER_OF_POSTS = 2 if TESTING_MODE else random.randint(3, 6)
# Post Intervals
TESTING_INTERVAL = 2  # in seconds
MIN_INTERVAL = 3600  # in seconds (2 hours between posts default)
# Project Config
# filepath to the ids we want to select from
ids_path = 'ids.txt'
# x account url prefix for posting to discord server
x_account_url = "https://vxtwitter.com/CryptoMonosNFT/status/"
# metadata url prefix to retrieve json containing trait attributes
json_metadata_url = "https://63kxpwhtce755f2i3qwxxmlmyosouz5mrucp3jclg2prh65ndiwq.arweave.net/9tV32PMRP96XSNwte7Fsw6TqZ6yNBP2kSzafE_utGi0/"
# image url prefix to retrieve .png images. *must have transparent background for random_hex_color() bacground to work
image_server_url = "https://storage.googleapis.com/cryptomonos/monos/"

# Print mode information
if TESTING_MODE:
    print(f"+--------- TESTING MODE [{NUMBER_OF_POSTS} POSTS] ---------+")

# X API KEYS stored in .env file
API_KEY = os.getenv('MAIN_API_KEY')
API_SECRET_KEY = os.getenv('MAIN_API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('MAIN_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('MAIN_ACCESS_TOKEN_SECRET')
# Discord Webhook URL
DISCORD_WEBHOOK_URL = os.getenv('MAIN_DISCORD_WEBHOOK_URL')

# Post to X function
def post_to_x(API_KEY, API_SECRET_KEY, message, media_id):
    payload = {"text": message, "media": {"media_ids": [str(media_id)]}}

    oauth = OAuth1Session(
        API_KEY,
        client_secret=API_SECRET_KEY,
        resource_owner_key=ACCESS_TOKEN,
        resource_owner_secret=ACCESS_TOKEN_SECRET,
    )

    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)

    if response.status_code != 201:
        raise Exception(f"Request returned an error: {response.status_code} {response.text}")

    return response.json()['data']

# Async function to post the vxtwitter url to discord channel via webhook
async def post_discord(post_url):
    if not ENABLE_POST_TO_DISCORD:
        return

    message_content = {"content": post_url}
    async with httpx.AsyncClient() as client:
        response = await client.post(DISCORD_WEBHOOK_URL, json=message_content)
        if response.status_code == 204:
            logging.info("Embed posted to Discord successfully.")
        else:
            logging.error(f"Failed to post embed to Discord: {response.status_code}")

# Async function to fetch metadata
async def fetch_metadata(random_mono_number):
    url = f"{json_metadata_url}{random_mono_number}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch metadata: {response.status_code}")

# Async function to generate message using OpenAI
async def generate_message(data):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Filter trait attributes in json
    ALLOWED_TRAIT_TYPES = {'Fur', 'Glasses', 'Hair', 'Hat', 'Jewelry', 'Mouth', 'Smoke'}
    type_value = None

    filtered_traits = [f"{attr['trait_type']}: {attr['value']}" for attr in data['attributes'] if attr['trait_type'] in ALLOWED_TRAIT_TYPES]
    type_value = next((attr['value'].strip() for attr in data['attributes'] if attr['trait_type'] == 'Type'), None)

    filtered_traits = random.sample(filtered_traits, min(3, len(filtered_traits)))

    traits = ', '.join(filtered_traits)
    templates = [
        f"You are a {type_value} posting a wild tweet to surprise your followers. Use two of these traits as inspiration to craft a creative tweet excluding the actual traits: {traits}. no hashtags and less than 25 words",
        f"Imagine being a {type_value} with traits like {traits}. Now create a tweet that highlights one of the traits and put a creative twist on it. no hashtags and less than 20 words",
        f"As a {type_value}, tweet about a feeling you’d have using one of these traits as inspiration: {traits}. Be creative with the start of your sentence. no hashtags and less than 25 words",
        f"As a {type_value}, describe your vibe using these traits values as guidance: {traits}. no hashtags and less than 20 words",
        f"You are a {type_value} giving life advice in a tweet. Use traits such as {traits} to add authenticity and depth to your advice. Make it witty and wise. no hashtags and less than 25 words"
    ]

    prompt = random.choice(templates)

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    return response.choices[0].message['content'], prompt, filtered_traits

async def refine_message(message):
    message = re.sub(r'\bjust\b', '', re.sub(r'\s#\S+', '', message.strip('"').strip('.').strip()))
    words = [word.lower() if 'Monos' not in word else word for word in message.split()]
    return ' '.join(words)

def calculate_intervals(number_of_posts, min_interval, total_hours=24):
    if TESTING_MODE:
        return [TESTING_INTERVAL] * number_of_posts
    
    remaining_time = total_hours * 3600 - (min_interval * number_of_posts)
    intervals = [min_interval + random.uniform(0, remaining_time) for _ in range(number_of_posts)]
    random.shuffle(intervals)
    return intervals

def format_duration(seconds):
    return str(timedelta(seconds=int(seconds)))

def read_numbers_from_file(filename):
    with open(filename, 'r') as file:
        return [int(line.replace(',', '').strip()) for line in file]

def setup_csv_writer(base_filename):
    date_str = datetime.datetime.now().strftime("%d_%m_%Y")
    csv_filename = f"{base_filename}_{date_str}.csv"

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["post_id", "metadata", "edition", "prompt", "filtered_traits", "refined_message"])
        writer.writeheader()

    return csv_filename

def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002600-\U000026FF"  # Miscellaneous Symbols
                               u"\U00002700-\U000027BF"  # Dingbats
                               u"\U00002B50-\U00002B59"  # Stars
                               u"\U00002300-\U000023FF"  # Miscellaneous Technical
                               u"\U0000203C-\U0000203C"  # Double exclamation mark
                               u"\U00002049-\U00002049"  # Exclamation question mark
                               u"\U00002194-\U0000219A"  # Arrow symbols
                               u"\U0001F1E6-\U0001F1FF"  # Flags
                               u"\U0001F004-\U0001F004"  # Mahjong Tile Red Dragon
                               u"\U0001F0CF-\U0001F0CF"  # Playing Card Black Joker
                               u"\U0001F201-\U0001F251"  # Enclosed characters
                               u"\U00002500-\U000025FF"  # Box Drawing
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def random_hex_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def contains_hashtag(message):
    return bool(re.search(r'\b#\w+', message))

def apply_background(image_path, hex_color):
    with Image.open(image_path) as img:
        background = Image.new('RGBA', img.size, hex_color)
        combined = Image.alpha_composite(background, img.convert('RGBA'))
        combined.save(image_path, 'PNG')

def display_results(csv_filename):
    try:
        df = pd.read_csv(csv_filename, encoding='utf-8', encoding_errors='replace')
        table = PrettyTable()
        table.field_names = ["edition", "refined_message"]
        for _, row in df.iterrows():
            edition_link = f'{image_server_url}{row["edition"]}.png'
            table.add_row([f'{edition_link}', row["refined_message"]])
        print(table)
    except UnicodeDecodeError as e:
        logging.error(f"UnicodeDecodeError: {e}")
        print(f"UnicodeDecodeError: {e}")
    except Exception as e:
        logging.error(f"Error reading the CSV file: {e}")
        print(f"Error reading the CSV file: {e}")

async def async_main():
    intervals = calculate_intervals(NUMBER_OF_POSTS, MIN_INTERVAL)

    if not TESTING_MODE:
        print(f"Number of posts: {NUMBER_OF_POSTS}")

    csv_filename = setup_csv_writer('posts_data.csv')
    with open(csv_filename, mode='a', newline='') as file:
        for i, interval in enumerate(intervals, 1):
            now = datetime.datetime.now()
            future_time = now + datetime.timedelta(seconds=interval)
            formatted_interval = format_duration(interval)
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Sleeping for {formatted_interval} until post {i} of {NUMBER_OF_POSTS} at {future_time.strftime('%Y-%m-%d %I:%M:%S %p')}.")
            await asyncio.sleep(interval)

            numbers_list = read_numbers_from_file(ids_path)
            random_mono_number = random.choice(numbers_list)
            metadata = await fetch_metadata(random_mono_number)

            for attempt in range(5):
                message, prompt, filtered_traits = await generate_message(metadata)
                refined_message = await refine_message(message)

                if refined_message.strip() and refined_message.strip()[0].isalpha() and not contains_hashtag(refined_message):
                    # print(f"Valid message: {refined_message}")
                    break
                else:
                    print(f"Invalid message on attempt {attempt + 1}, retrying...")

                if attempt == 4:
                    print("Failed to generate a valid message after 5 attempts.")
                    break

            cleaned_message = remove_emojis(refined_message)

            try:
                writer = csv.DictWriter(file, fieldnames=["post_id", "metadata", "edition", "prompt", "filtered_traits", "refined_message"])
                writer.writerow({
                    "post_id": i,
                    "metadata": json.dumps(metadata),
                    "edition": metadata['edition'],
                    "prompt": prompt,
                    "filtered_traits": ', '.join(filtered_traits),
                    "refined_message": cleaned_message
                })
            except UnicodeEncodeError:
                writer.writerow({
                    "post_id": i,
                    "metadata": json.dumps(metadata),
                    "edition": metadata['edition'],
                    "prompt": prompt,
                    "filtered_traits": ', '.join(filtered_traits),
                    "refined_message": "emoji_error"
                })

            image_url = f"{image_server_url}{random_mono_number}.png"
            response_image = requests.get(image_url)

            if response_image.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.png') as temp_file:
                    temp_file.write(response_image.content)
                    image_path = temp_file.name

                hex_color = random_hex_color()
                apply_background(image_path, hex_color)

                try:
                    with open(image_path, "rb") as img_file:
                        img_data = img_file.read()
                        media_upload_url = 'https://upload.twitter.com/1.1/media/upload.json'
                        response = requests.post(media_upload_url, auth=OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET), files={'media': img_data})

                        if response.status_code == 200:
                            media_id = response.json()['media_id']
                        else:
                            print(f'Error uploading media: {response.status_code} - {response.text}')

                        if ENABLE_POST_TO_X:
                            try:
                                x_data = post_to_x(API_KEY, API_SECRET_KEY, refined_message, media_id)
                                post_id = x_data['id']
                                post_url = f"{x_account_url}{post_id}"
                                await post_discord(post_url)
                            except Exception as e:
                                print(f"An error occurred when posting to X: {e}")
                finally:
                    os.remove(image_path)

    display_results(csv_filename)

if __name__ == "__main__":
    asyncio.run(async_main())