from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from main import ProductivityScraper
import requests

app = Flask(__name__)
CORS(app)

BREVO_API_KEY = os.environ.get("BREVO_API_KEY")  # Safer way to load secrets


@app.route("/")
def home():
    return "Productivity Scraper API is running!"


@app.route("/api/content", methods=["POST"])
def get_content_post():
    try:
        data = request.get_json(force=True)
        tags = data.get("tags", [])
        scraper = ProductivityScraper()
        (
            article_titles,
            article_sources,
            article_urls,
            video_titles,
            video_channels,
            video_urls,
        ) = scraper.get_recommendations_based_on_tags(tags)

        return jsonify(
            {
                "article_titles": article_titles,
                "article_sources": article_sources,
                "article_urls": article_urls,
                "video_titles": video_titles,
                "video_channels": video_channels,
                "video_urls": video_urls,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/send-newsletter", methods=["POST"])
def send_newsletter():
    data = request.json
    email = data.get("email")
    tags = data.get("tags", [])

    if not email or not tags:
        return jsonify({"error": "Missing email or tags"}), 400

    # Create simple HTML content
    content = f"""
    <h2>Your Personalized Productivity Newsletter</h2>
    <p>Here are your selected topics:</p>
    <ul>
        {''.join(f"<li>{tag}</li>" for tag in tags)}
    </ul>
    <p>We’ll be adding curated content here in future updates.</p>
    """

    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "sender": {
            "name": "Bytecode Curator",
            "email": "anuragforwork0018@gmail.com",
        },
        "to": [{"email": email}],
        "subject": "🎯 Your Personalized Productivity Newsletter from Bytecode",
        "htmlContent": content,
    }

    res = requests.post(
        "https://api.brevo.com/v3/smtp/email", headers=headers, json=payload
    )

    if res.status_code != 201:
        return jsonify({"error": "Failed to send email", "details": res.text}), 500

    return jsonify({"message": "Newsletter sent!"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
