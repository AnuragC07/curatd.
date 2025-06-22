from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from main import ProductivityScraper

app = Flask(__name__)
CORS(app)


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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
