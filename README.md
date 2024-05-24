"# xbot" 
# X Bot

This repository contains a Python script that automates posting to X (formerly known as Twitter) and Discord. The script uses the OpenAI API to generate creative messages, fetches metadata and images, and posts them to social media.

## Features
- Automated posting to X and Discord
- Metadata fetching and image processing
- Creative message generation using OpenAI
- Supports testing mode for safe testing

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