# 🤖 AI News Bot for Blogger

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)

An automated content pipeline that fetches the latest news, uses Google's Gemini AI to write unique articles, and posts them directly to a Blogspot blog every hour. This project is a powerful demonstration of API orchestration and AI-driven content creation.

**👉 Live Demo Blog: [chaibuzz.blogspot.com](https://chaibuzz.blogspot.com)**

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [⚙️ How It Works](#%EF%B8%8F-how-it-works)
- [🚀 Setup and Installation](#-setup-and-installation)
- [☁️ Deployment on Render](#%EF%B8%8F-deployment-on-render)
- [⏰ Automation with Make.com](#-automation-with-makecom)
- [🤝 Contributing](#-contributing)
- [📜 License](#license)

---

## ✨ Features

* **Automated News Fetching**: Pulls recent news articles from various categories using the [World News API](https://worldnewsapi.com/).
* **AI-Powered Writing**: Leverages Google's **Gemini AI** to analyze multiple articles and generate a brand-new, comprehensive, and engaging blog post.
* **Automatic Publishing**: Seamlessly posts the generated article, including a title, HTML content, labels (tags), and a relevant image, to any Blogspot blog using the Blogger API v3.
* **Cloud-Deployable**: Built with Flask, it's designed to be deployed on cloud platforms like Render.
* **Scheduler Ready**: Includes a simple `/run` endpoint to be triggered by cron job services like Make.com, EasyCron, or GitHub Actions.

---

## ⚙️ How It Works

The automation follows a simple yet powerful three-step process, which is triggered externally by a scheduler.



1.  **Trigger**: An external service like **[Make.com](https://www.make.com/)** sends a scheduled HTTP GET request to the `/run` endpoint of our Flask application hosted on **[Render.com](https://render.com/)**. This happens every hour.
2.  **Fetch & Generate**:
    * The bot fetches 30 recent news articles from a random category via the **World News API**.
    * These articles are passed to the **Gemini AI** with a specific prompt instructing it to act as a news editor and write a new, detailed article in a structured JSON format.
3.  **Publish**:
    * The bot parses the JSON output from Gemini.
    * It authenticates with the **Google Blogger API** using OAuth2.
    * Finally, it publishes the new title, HTML content, labels, and a selected image to the specified Blogspot blog.

---

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **AI Model**: Google Gemini AI
* **APIs**: World News API, Google Blogger API v3
* **Hosting**: Render
* **Automation/Scheduler**: Make.com

---

## 🚀 Setup and Installation

Follow these steps to get your own AI News Bot up and running.

### 1. Prerequisites

* Python 3.9+
* Git
* A Google Account with a Blogspot blog created.

### 2. Clone the Repository

```bash
git clone https://github.com/iAmVSJ0702/chaibuzz-news-bot.git
cd chaibuzz-news-bot
```

### 3. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. API Keys and Credentials

You'll need to get credentials for three services.

* **Google Blogger API**:
    1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
    2.  Create a new project.
    3.  Enable the **"Blogger API v3"**.
    4.  Go to "Credentials", click "Create Credentials", and choose "OAuth client ID".
    5.  Select "Desktop application" as the application type.
    6.  Download the JSON file and rename it to `client_secret.json` in the root of your project directory.

* **World News API**:
    1.  Sign up for a free account at [worldnewsapi.com](https://worldnewsapi.com/).
    2.  Get your API key from your dashboard.

* **Google Gemini AI API**:
    1.  Go to [Google AI Studio](https://aistudio.google.com/).
    2.  Click on "Get API key" and create a new key.

### 6. Configure Environment Variables

Create a file named `.env` in the root directory and add the following variables.

```.env
# --- API Keys ---
WORLDNEWS_API_KEY="YOUR_WORLDNEWS_API_KEY"
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# --- Blogger Config ---
BLOG_URL="[https://your-blog-name.blogspot.com/](https://your-blog-name.blogspot.com/)"

# --- File Paths (Defaults are usually fine) ---
CLIENT_SECRET_FILE="client_secret.json"
STORAGE_FILE="credentials.storage"

# --- Scopes (Default is correct for Blogger) ---
BLOGGER_SCOPES="[https://www.googleapis.com/auth/blogger](https://www.googleapis.com/auth/blogger)"
```
*(Note: If you are deploying to a service like Render, you will set these in the environment variables section of your service dashboard instead of using a `.env` file.)*

### 7. First-Time Authentication with Google

Before you can automate posts, you need to run an initial authorization flow to generate your `credentials.storage` file.

Run the script locally from your terminal:

```bash
python news_bot.py --noauth_local_webserver
```

* A URL will be printed to your console. Copy and paste it into your browser.
* Log in with the Google account that owns your Blogspot blog.
* Grant the requested permissions.
* You will be redirected to a page with an authorization code. Copy this code.
* Paste the code back into your terminal and press Enter.

A file named `credentials.storage` will be created. **This file proves you are authenticated.**

---

## ☁️ Deployment on Render

This application is ready for deployment on a free Render web service.

1.  **Push your code** to a GitHub repository (including the `credentials.storage` file).
2.  On the Render dashboard, create a new **Web Service**.
3.  Connect the GitHub repository you just created.
4.  Set the following configuration:
    * **Environment**: `Python 3`
    * **Build Command**: `pip install -r requirements.txt`
    * **Start Command**: `gunicorn news_bot:app`
5.  Go to the **"Environment"** tab and add all the secrets from your `.env` file (`WORLDNEWS_API_KEY`, `GEMINI_API_KEY`, `BLOG_URL`).
6.  Click **"Create Web Service"**. Render will deploy your application.

---

## ⏰ Automation with Make.com

To run the bot every hour, use a free scheduling service like Make.com.

1.  Create a new Scenario in Make.com.
2.  The first module should be a **Timer** (e.g., "Every Day" and set the time interval to every 60 minutes).
3.  The second module should be an **HTTP** module set to "Make a request".
4.  Configure the HTTP request:
    * **URL**: Your Render application URL, followed by `/run`. For example: `https://your-app-name.onrender.com/run`
    * **Method**: `GET`
5.  Turn on the scenario. It will now trigger your bot every hour to post a new article!

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, please feel free to create an issue or submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the **GNU General Public License v3.0**. See 'LICENSE' for more information.
