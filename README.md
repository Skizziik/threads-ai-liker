# Threads AI Liker

This is a Python script that uses Playwright to automate liking posts on Threads.net based on a specific search query. The bot is designed to like posts that have a low number of likes, making it useful for discovering and engaging with new or unpopular content on a specific topic.

## Features

-   **Automated Liking:** Automatically likes posts based on a search term.
-   **Smart Session Management:** On the first run, it allows you to log in manually. It then saves your session data, so you don't need to log in again for subsequent runs. No need to store your password in the script!
-   **Configurable:** Easily change the search query, like cooldown, and the maximum number of likes a post can have to be considered for a "like".
-   **Rate-Limit Aware:** Includes a configurable cooldown between likes to reduce the risk of account suspension.
-   **Debugging:** Saves a screenshot on startup (`debug_screenshot.png`) to help with troubleshooting.

## Prerequisites

-   Python 3.7+
-   Pip (Python package installer)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Skizziik/threads-ai-liker.git
    cd threads-ai-liker
    ```

2.  **Install the required Python libraries:**
    ```bash
    pip install playwright
    ```

3.  **Install the Playwright browser binaries:**
    ```bash
    playwright install
    ```

## How to Use

### First-Time Setup (Manual Login)

1.  Run the script from your terminal:
    ```bash
    python threads_liker.py
    ```
2.  A new Chromium browser window will open. The script will pause and ask you to log into your Threads.net account.
3.  Log in as you normally would.
4.  After you have successfully logged in, **close the browser window**.
5.  The script will detect that the browser has been closed, and it will create a `user_data` directory containing your session information. It will then exit.

### Subsequent Runs (Automated Liking)

1.  Run the script again:
    ```bash
    python threads_liker.py
    ```
2.  The script will now use your saved session data to open Threads, perform the search, and start liking posts automatically. You can watch it work in the browser window.

## Configuration

You can customize the bot's behavior by editing the settings at the top of the `threads_liker.py` file:

-   `SEARCH_QUERY`: The topic to search for (e.g., `"art"`, `"python"`). Default is `"ai"`.
-   `MAX_LIKES_TO_LIKE`: The script will only like posts that have fewer likes than this number. Default is `5`.
-   `LIKE_COOLDOWN_SECONDS`: The number of seconds to wait between each like. Default is `20`.
-   `USER_DATA_DIR`: The directory where session data is stored. Default is `"./user_data"`.

### Important Note on Selectors

This script relies on CSS selectors to find elements on the Threads website (like posts and buttons). Social media websites change their code frequently, which can break the script.

If the script stops working, you may need to update the CSS selectors at the top of the file. The comments in the code provide guidance on which selectors might need to be changed. For example, the `aria-label` for the "Like" button might change from `'Нравится'` (Russian) to `'Like'` (English) depending on your account's language settings.

## Disclaimer

Automating social media interactions can be against the terms of service of the platform. Use this script at your own risk. The developer is not responsible for any consequences, including but not limited to account suspension or banning.
