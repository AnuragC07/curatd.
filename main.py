#!/usr/bin/env python3
"""
Daily Productivity Content Scraper
Scrapes articles and YouTube videos on productivity and life improvement topics
"""

import requests
from bs4 import BeautifulSoup
import yt_dlp
import random
import time
from urllib.parse import urljoin, urlparse
import re


class ProductivityScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Article sources
        self.article_sources = [
            "https://zenhabits.net",
            "https://www.lifehacker.com/tag/productivity",
            "https://medium.com/tag/productivity",
            "https://www.fastcompany.com/section/work-life",
            "https://hbr.org/topic/productivity",
            "https://www.inc.com/topic/productivity",
        ]

        # YouTube channels focused on productivity/self-improvement
        self.youtube_channels = [
            "https://www.youtube.com/@aliabdaal/videos",
            "https://www.youtube.com/@thomasfrank/videos",
            "https://www.youtube.com/@mattdavella/videos",
            "https://www.youtube.com/@betterideas/videos",
            "https://www.youtube.com/@TheModernHealthspan/videos",
        ]

        # Keywords for filtering relevant content
        self.keywords = [
            "productivity",
            "habits",
            "morning routine",
            "time management",
            "focus",
            "discipline",
            "goals",
            "motivation",
            "mindset",
            "self improvement",
            "personal development",
            "efficiency",
            "life improvement",
            "better life",
            "success",
            "growth",
        ]

    def is_relevant_content(self, text):
        """Check if content is relevant to productivity/life improvement"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

    def scrape_article_links(self, url):
        """Scrape article links from a given URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Common selectors for article links
            article_links = []

            # Try different selectors
            selectors = [
                "article a[href]",
                ".post-title a[href]",
                ".entry-title a[href]",
                "h2 a[href]",
                "h3 a[href]",
                ".article-title a[href]",
                ".headline a[href]",
            ]

            for selector in selectors:
                links = soup.select(selector)
                if links:
                    for link in links[:10]:  # Limit to first 10
                        href = link.get("href")
                        title = link.get_text().strip()
                        if href and title and self.is_relevant_content(title):
                            full_url = urljoin(url, href)
                            article_links.append(
                                {
                                    "title": title,
                                    "url": full_url,
                                    "source": urlparse(url).netloc,
                                }
                            )
                    break

            return article_links[:5]  # Return top 5

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def get_youtube_videos(self, channel_url):
        """Get recent videos from a YouTube channel"""
        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "playlistend": 20,  # Get recent 20 videos
                "no_warnings": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(channel_url, download=False)

                videos = []
                if "entries" in playlist_info:
                    for entry in playlist_info["entries"]:
                        if entry and "title" in entry:
                            title = entry.get("title", "")
                            if self.is_relevant_content(title):
                                videos.append(
                                    {
                                        "title": title,
                                        "url": f"https://www.youtube.com/watch?v={entry['id']}",
                                        "channel": playlist_info.get(
                                            "uploader", "Unknown"
                                        ),
                                    }
                                )

                return videos[:3]  # Return top 3 relevant videos

        except Exception as e:
            print(f"Error getting videos from {channel_url}: {e}")
            return []

    def scrape_articles(self, count=2):
        """Scrape specified number of articles"""
        all_articles = []

        print("🔍 Searching for productivity articles...")

        for source in self.article_sources:
            articles = self.scrape_article_links(source)
            all_articles.extend(articles)
            time.sleep(1)  # Be respectful with requests

            if len(all_articles) >= count * 3:  # Get extra to filter from
                break

        # Remove duplicates and shuffle
        unique_articles = []
        seen_titles = set()
        for article in all_articles:
            if article["title"] not in seen_titles:
                unique_articles.append(article)
                seen_titles.add(article["title"])

        # Return random selection
        random.shuffle(unique_articles)
        return unique_articles[:count]

    def scrape_videos(self, count=2):
        """Scrape specified number of YouTube videos"""
        all_videos = []

        print("🎥 Searching for productivity videos...")

        for channel in self.youtube_channels:
            videos = self.get_youtube_videos(channel)
            all_videos.extend(videos)
            time.sleep(2)  # Be respectful with requests

            if len(all_videos) >= count * 3:  # Get extra to filter from
                break

        # Remove duplicates and shuffle
        unique_videos = []
        seen_titles = set()
        for video in all_videos:
            if video["title"] not in seen_titles:
                unique_videos.append(video)
                seen_titles.add(video["title"])

        # Return random selection
        random.shuffle(unique_videos)
        return unique_videos[:count]

    def get_daily_content(self):
        """Get daily curated content bundle"""
        print("🚀 Getting your daily productivity content...\n")

        # Get articles and videos
        articles = self.scrape_articles(2)
        videos = self.scrape_videos(2)

        return articles, videos

    def display_content(self, articles, videos):
        """Display the curated content in a nice format"""
        print("=" * 60)
        print("📚 HERE IS YOUR DAILY CURATED CONTENT 📚")
        print("=" * 60)
        print()

        if articles:
            print("📖 PRODUCTIVITY ARTICLES:")
            print("-" * 30)
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Link: {article['url']}")
                print()
        else:
            print("📖 No articles found today. Try again later!")
            print()

        if videos:
            print("🎥 LIFE IMPROVEMENT VIDEOS:")
            print("-" * 30)
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['title']}")
                print(f"   Channel: {video['channel']}")
                print(f"   Link: {video['url']}")
                print()
        else:
            print("🎥 No videos found today. Try again later!")
            print()

        print("=" * 60)
        print("💡 Enjoy your learning journey!")
        print("=" * 60)


def main():
    """Main function to run the scraper"""
    scraper = ProductivityScraper()

    try:
        articles, videos = scraper.get_daily_content()
        scraper.display_content(articles, videos)
    except KeyboardInterrupt:
        print("\n❌ Scraping cancelled by user")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        print("Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
