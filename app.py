from flask import Flask, jsonify
from flask_cors import CORS
import os
from main import ProductivityScraper

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Productivity Scraper API is running!"


@app.route("/api/content")
def get_content():
    try:
        scraper = ProductivityScraper()
        articles, videos = scraper.get_daily_content()

        return jsonify({"articles": articles, "videos": videos})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
