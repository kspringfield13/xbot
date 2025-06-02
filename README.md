# xBot
xBot is a Python script designed to automate content publication on X and Discord. It leverages the OpenAI API to generate concise, creative messages based on on‐chain NFT metadata, fetches associated images, applies a randomized background color, and posts the results on social media.

## Features
- Automated Posting: Schedules and publishes multiple posts per day to both X and Discord, with a “test” mode for safe dry runs.
- Creative Message Generation: Queries OpenAI to craft short, on-brand tweets using a set of filtered NFT traits (e.g., Fur, Hair, Hat).
- Metadata & Image Handling: Pulls JSON metadata from a configurable endpoint, downloads the PNG image, then composites it over a random hex-color background.
- Configurable Rate Limits: Allows you to specify how many posts to send, minimum intervals between posts, and separate modes for testing versus production.
- CSV Logging & Preview: Saves each generated post (metadata, prompt, and cleaned message) to a date-stamped CSV—and prints a simple table of edition links and final messages once the run completes.

## Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/kspringfield13/xbot.git
cd xbot
pip install -r requirements.txt
```

## Configuration

Create a .env file in the project root directory and add your API keys and discord webhook URLs:

```bash
MAIN_API_KEY=your_x_api_key
MAIN_API_SECRET_KEY=your_x_api_secret_key
MAIN_ACCESS_TOKEN=your_x_access_token
MAIN_ACCESS_TOKEN_SECRET=your_x_access_token_secret
MAIN_DISCORD_WEBHOOK_URL=your_discord_webhook_url
OPENAI_API_KEY=your_openai_api_key
```

Finish updating configuration within xbot.py for further customizations:

```python
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
x_account_url = "<x account url here>/status/"
# metadata url prefix to retrieve json containing trait attributes
json_metadata_url = "<metadata url here>"
# image url prefix to retrieve .png images. *must have transparent background for random_hex_color() bacground to work
image_server_url = "<image url here>"
```

## Usage

To run the script in test mode:

```bash
python xbot.py test
```

To run the script in production mode:

```bash
python xbot.py run
```

## Sample Output

When running the script in test mode:

```bash
C:\Users\kspri\Dev\xbot>python xbot.py test
+--------- TESTING MODE [2 POSTS] ---------+
2024-05-24 10:47:30 - Sleeping for 0:00:02 until post 1 of 2 at 2024-05-24 10:47:32 AM.
2024-05-24 10:47:32,674 - INFO - HTTP Request: GET https://63kxpwhtce755f2i3qwxxmlmyosouz5mrucp3jclg2prh65ndiwq.arweave.net/9tV32PMRP96XSNwte7Fsw6TqZ6yNBP2kSzafE_utGi0/5088 "HTTP/1.1 200 OK"
2024-05-24 10:47:34 - Sleeping for 0:00:02 until post 2 of 2 at 2024-05-24 10:47:36 AM.
2024-05-24 10:47:37,031 - INFO - HTTP Request: GET https://63kxpwhtce755f2i3qwxxmlmyosouz5mrucp3jclg2prh65ndiwq.arweave.net/9tV32PMRP96XSNwte7Fsw6TqZ6yNBP2kSzafE_utGi0/6318 "HTTP/1.1 200 OK"
+-----------------------------------------------------------+------------------------------------------------------------------------------+
|                          edition                          |                               refined_message                                |
+-----------------------------------------------------------+------------------------------------------------------------------------------+
| https://storage.googleapis.com/cryptomonos/monos/5088.png |                 sleek and adventurous with a touch of charm                  |
| https://storage.googleapis.com/cryptomonos/monos/6318.png | even a lily pad needs patience to float; leap wisely and savor each ripple.  |
+-----------------------------------------------------------+------------------------------------------------------------------------------+
```
