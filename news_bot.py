# news_bot_flask.py
import os
import random
import json
import httplib2
from flask import Flask
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser
from googleapiclient import discovery
from google import genai
import worldnewsapi
from worldnewsapi.rest import ApiException

app = Flask(__name__)

# ------------------- CONFIG -------------------
CLIENT_SECRET_FILE = os.environ.get("CLIENT_SECRET_FILE", "client_secret.json")
STORAGE_FILE = os.environ.get("STORAGE_FILE", "credentials.storage")
BLOG_URL = os.environ.get("BLOG_URL", "https://chaibuzz.blogspot.com/")
SCOPES = os.environ.get("BLOGGER_SCOPES", "https://www.googleapis.com/auth/blogger")
WORLDNEWS_API_KEY = os.environ.get("WORLDNEWS_API_KEY", "YOUR_DEFAULT_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_DEFAULT_KEY")

# Init Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Init WorldNews API client
newsapi_configuration = worldnewsapi.Configuration(api_key={'apiKey': WORLDNEWS_API_KEY})
newsapi_instance = worldnewsapi.NewsApi(worldnewsapi.ApiClient(newsapi_configuration))

# ------------------- Blogger Auth -------------------
def authorize_credentials():
    print("🔑 Authorizing Blogger credentials...")
    storage = Storage(STORAGE_FILE)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        print("⚠️ No valid credentials found, running auth flow...")
        flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=SCOPES)
        credentials = run_flow(flow, storage, flags=argparser.parse_args(args=['--noauth_local_webserver']))
    print("✅ Blogger credentials ready.")
    return credentials

def get_blogger_service():
    print("🔗 Connecting to Blogger API...")
    credentials = authorize_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('blogger', 'v3', http=http)
    print("✅ Blogger API connected.")
    return service

def get_blog_id(service, blog_url):
    print(f"📌 Getting blog ID for: {blog_url}")
    blog = service.blogs().getByUrl(url=blog_url).execute()
    blog_id = blog["id"]
    print(f"✅ Blog ID: {blog_id}")
    return blog_id

# ------------------- Step 1: Fetch random news -------------------
def fetch_random_news(number=30, country="in"):
    categories = [
        "politics", "sports", "business", "technology", "entertainment",
        "health", "science", "lifestyle", "travel", "culture", "education", "environment"
    ]
    category = random.choice(categories)
    print(f"📰 Fetching {number} news articles from {country} in category: {category}")

    try:
        response = newsapi_instance.search_news(
            source_country=country,
            language="en",
            categories=category,
            sort="publish-time",
            sort_direction="desc",
            number=number
        )
        articles = []
        for art in response.news:
            articles.append({
                "id": art.id,
                "title": art.title,
                "text": art.text,
                "summary": art.summary,
                "url": art.url,
                "image": art.image,
                "video": art.video,
                "publish_date": art.publish_date,
                "authors": art.authors,
                "language": art.language,
                "source_country": art.source_country,
                "sentiment": art.sentiment
            })
        print(f"✅ Retrieved {len(articles)} articles.")
        return articles
    except ApiException as e:
        print(f"❌ Error fetching news: {e}")
        return []

# ------------------- Step 2: Generate post using Gemini -------------------
def generate_post(articles):
    print("🤖 Generating post using Gemini...")
    prompt = f"""
    You are a news editor. Using the following {len(articles)} articles:

    {json.dumps(articles, indent=2)}

    Write a NEW detailed news post, with in-depth content and a catchy title, i want a click bait title.
    STRICTLY return valid JSON in this format:

    {{
      "title": "Catchy blog title",
      "content": "<p>Full HTML formatted blog content...</p>",
      "labels": ["tag1", "tag2", "tag3"]
    }}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    try:
        data = json.loads(response.text)
        print("✅ Gemini JSON parsed successfully.")
        return data
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            print("⚠️ Extracted valid JSON from Gemini output.")
            return json.loads(match.group(0))
        raise

# ------------------- Step 3: Post to Blogger -------------------
def post_to_blogger(title, content, labels=None, image_url=None):
    service = get_blogger_service()
    blog_id = get_blog_id(service, BLOG_URL)

    payload = {
        'title': title,
        'content': content,
        'labels': labels or []
    }

    if image_url:
        payload['images'] = [{'url': image_url}]

    print("🚀 Posting to Blogger...")
    post = service.posts().insert(blogId=blog_id, body=payload).execute()
    print(f"✅ Post published: {post['url']}")
    return post

# ------------------- MAIN BOT FUNCTION -------------------
def run_bot():
    print("=== 📢 STARTING NEWS BOT ===")
    articles = fetch_random_news(number=30, country="in")
    gemini_output = generate_post(articles)

    image_url = None
    if gemini_output.get("image_source_id"):
        for art in articles:
            if str(art.get("id")) == str(gemini_output["image_source_id"]):
                if art.get("image"):
                    image_url = art["image"]
                break

    post_to_blogger(
        title=gemini_output["title"],
        content=gemini_output["content"],
        labels=gemini_output.get("labels", []),
        image_url=image_url
    )
    print("=== 🎉 NEWS BOT FINISHED ===")

# ------------------- FLASK ROUTE -------------------
@app.route("/run")
def run_endpoint():
    run_bot()
    return "✅ Bot run completed!"

# ------------------- RUN FLASK -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)
