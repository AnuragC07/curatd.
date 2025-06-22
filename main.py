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
import json
import os
from datetime import datetime, timedelta
import hashlib


class ProductivityScraper:
    def __init__(self):
        # Randomize user agents for better scraping
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]

        # File to store previous recommendations
        self.history_file = "scraper_history.json"
        self.load_history()

        # Scraper-friendly article sources (removed problematic ones)
        self.article_sources = [
            # Blog-style sites (generally scraper-friendly)
            "https://zenhabits.net",
            "https://jamesclear.com/articles",
            "https://www.calnewport.com/blog/",
            "https://sethgodin.typepad.com",
            "https://www.scotthyoung.com/blog/",
            "https://www.asian-efficiency.com/blog/",
            "https://blog.rescuetime.com",
            "https://blog.todoist.com",
            "https://blog.doist.com",
            "https://www.timemanagementninja.com",
            "https://www.developgoodhabits.com/blog/",
            "https://www.pickthebrain.com/blog/",
            "https://www.lifehack.org/articles/productivity",
            "https://www.productivityist.com",
            "https://www.habitsforwellbeing.com/blog/",
            "https://focusedx.com/blog/",
            "https://noisli.com/blog/",
            # Medium articles (RSS-friendly)
            "https://medium.com/tag/productivity",
            "https://medium.com/tag/time-management",
            "https://medium.com/tag/self-improvement",
            "https://medium.com/tag/habits",
            "https://medium.com/tag/goal-setting",
            "https://medium.com/tag/work-life-balance",
            # Corporate blogs (usually have RSS)
            "https://blog.trello.com",
            "https://blog.asana.com",
            "https://blog.monday.com",
            "https://zapier.com/blog",
            "https://blog.clockify.me",
            "https://www.toggl.com/blog",
            "https://blog.evernote.com",
            "https://www.wrike.com/blog",
            "https://blog.hubspot.com",
            # News/Magazine style (with RSS)
            "https://www.entrepreneur.com/topic/productivity",
            "https://www.inc.com/topic/productivity",
            "https://www.fastcompany.com/section/work-life",
            "https://www.themuse.com/advice/productivity",
            "https://www.makeuseof.com/tag/productivity/",
            "https://www.howtogeek.com/tag/productivity/",
            # Specialized productivity sites
            "https://gettingthingsdone.com/blog/",
            "https://www.franklincovey.com/blog/",
            "https://www.goals.com/blog",
            "https://www.goalcast.com/category/success/",
            "https://www.artofmanliness.com/category/career-wealth/",
            "https://www.bulletjournal.com/blogs/bulletjournalist",
            # Health and wellness (productivity-related)
            "https://www.sleepfoundation.org/news",
            "https://www.mayoclinic.org/healthy-lifestyle",
            "https://www.healthline.com/health/mental-health",
            # Remote work and career
            "https://remote.co/blog/",
            "https://blog.remoteyear.com",
            "https://www.flexjobs.com/blog/",
            "https://blog.ynab.com",
            # Learning platforms
            "https://blog.coursera.org",
            "https://blog.udemy.com",
            "https://www.skillshare.com/blog/",
        ]

        # YouTube channels (maintained from original)
        self.youtube_channels = [
            # Original channels
            "https://www.youtube.com/@aliabdaal/videos",
            "https://www.youtube.com/@thomasfrank/videos",
            "https://www.youtube.com/@mattdavella/videos",
            "https://www.youtube.com/@betterideas/videos",
            "https://www.youtube.com/@TheModernHealthspan/videos",
            # Requested specific channels
            "https://www.youtube.com/@zachhighley/videos",
            "https://www.youtube.com/@sankhokun/videos",
            "https://www.youtube.com/@TEDx/videos",
            "https://www.youtube.com/@hubermanlab/videos",
            # Major productivity and business channels
            "https://www.youtube.com/@TED/videos",
            "https://www.youtube.com/@TEDEd/videos",
            "https://www.youtube.com/@BigThink/videos",
            "https://www.youtube.com/@AsapSCIENCE/videos",
            "https://www.youtube.com/@thebrainscoop/videos",
            # Time management and productivity specialists
            "https://www.youtube.com/@CalNewportMedia/videos",
            "https://www.youtube.com/@pickupslimes/videos",
            "https://www.youtube.com/@AmyLandino/videos",
            "https://www.youtube.com/@ProductivityGame/videos",
            "https://www.youtube.com/@KeepProductive/videos",
            "https://www.youtube.com/@TheProductivityist/videos",
            # Study and learning techniques
            "https://www.youtube.com/@CrashCourse/videos",
            "https://www.youtube.com/@StudyTee/videos",
            "https://www.youtube.com/@TheStudyCorner/videos",
            "https://www.youtube.com/@StudyMD/videos",
            "https://www.youtube.com/@studywithme/videos",
            "https://www.youtube.com/@MartyLobdell/videos",
            # Health and wellness for productivity
            "https://www.youtube.com/@DocMikeEvans/videos",
            "https://www.youtube.com/@DrRanjanChatterjee/videos",
            "https://www.youtube.com/@drmarkhyman/videos",
            "https://www.youtube.com/@FoundMyFitness/videos",
            "https://www.youtube.com/@SigmaStudio/videos",
            # Business and entrepreneurship
            "https://www.youtube.com/@GaryVee/videos",
            "https://www.youtube.com/@TheTimFerrissShow/videos",
            "https://www.youtube.com/@TonyRobbins/videos",
            "https://www.youtube.com/@RobinSharma/videos",
            "https://www.youtube.com/@BrianTracy/videos",
            "https://www.youtube.com/@grant.cardone/videos",
            # Minimalism and life optimization
            "https://www.youtube.com/@TheMinimalists/videos",
            "https://www.youtube.com/@MuchelleB/videos",
            "https://www.youtube.com/@JordanPageStuff/videos",
            "https://www.youtube.com/@ClutterBug/videos",
            "https://www.youtube.com/@mariekondo/videos",
            # Tech and digital productivity
            "https://www.youtube.com/@MKBHD/videos",
            "https://www.youtube.com/@UnboxTherapy/videos",
            "https://www.youtube.com/@TheVerge/videos",
            "https://www.youtube.com/@Androidauthority/videos",
            "https://www.youtube.com/@9to5Google/videos",
            # Finance and career
            "https://www.youtube.com/@TheFinancialDiet/videos",
            "https://www.youtube.com/@GrahamStephan/videos",
            "https://www.youtube.com/@BenFelixCSI/videos",
            "https://www.youtube.com/@ThePlainBagel/videos",
            # Motivation and mindset
            "https://www.youtube.com/@motiversity/videos",
            "https://www.youtube.com/@MulliganBrothers/videos",
            "https://www.youtube.com/@JimKwik/videos",
            "https://www.youtube.com/@MindsetMentorPodcast/videos",
            "https://www.youtube.com/@Goalcast/videos",
            # Science and psychology
            "https://www.youtube.com/@veritasium/videos",
            "https://www.youtube.com/@3blue1brown/videos",
            "https://www.youtube.com/@Vsauce/videos",
            "https://www.youtube.com/@SciShow/videos",
            "https://www.youtube.com/@CGPGrey/videos",
            # Habit formation and behavior change
            "https://www.youtube.com/@JamesClear/videos",
            "https://www.youtube.com/@BetterThanYesterday/videos",
            "https://www.youtube.com/@ImprovementPill/videos",
            "https://www.youtube.com/@selfimprovementDaily/videos",
            "https://www.youtube.com/@WhatIveLearned/videos",
            # Creative and design thinking
            "https://www.youtube.com/@TheStoryOfStuff/videos",
            "https://www.youtube.com/@ideo/videos",
            "https://www.youtube.com/@TheArtAssignment/videos",
            "https://www.youtube.com/@Vox/videos",
            "https://www.youtube.com/@Numberphile/videos",
            # Additional high-value productivity channels
            "https://www.youtube.com/@AndrewHuberman/videos",
            "https://www.youtube.com/@PowerfulJRE/videos",
            "https://www.youtube.com/@lexfridman/videos",
            "https://www.youtube.com/@TheKnowledgeProject/videos",
            "https://www.youtube.com/@NavalRavikant/videos",
            "https://www.youtube.com/@samharrisorg/videos",
            "https://www.youtube.com/@theartofimprovement/videos",
            "https://www.youtube.com/@FightMediocrity/videos",
            "https://www.youtube.com/@OnePercentBetter/videos",
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
            "workflow",
            "organization",
            "planning",
            "routine",
            "meditation",
            "mindfulness",
            "deep work",
            "flow state",
            "energy",
            "wellness",
            "balance",
            "procrastination",
            "stress",
            "anxiety",
        ]

    def get_random_headers(self):
        """Get randomized headers for scraping"""
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def load_history(self):
        """Load previous recommendations history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    self.history = json.load(f)
            else:
                self.history = {"articles": [], "videos": [], "last_update": ""}
        except:
            self.history = {"articles": [], "videos": [], "last_update": ""}

    def save_history(self):
        """Save current recommendations to history"""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")

    def get_content_hash(self, content):
        """Generate hash for content to check duplicates"""
        content_str = f"{content.get('title', '')}_{content.get('url', '')}"
        return hashlib.md5(content_str.encode()).hexdigest()

    def is_content_recent(self, content):
        """Check if content was recommended recently"""
        content_hash = self.get_content_hash(content)
        content_type = "articles" if "source" in content else "videos"

        # Check if content was recommended in last 7 days
        recent_hashes = [
            item.get("hash") for item in self.history.get(content_type, [])[-50:]
        ]
        return content_hash in recent_hashes

    def is_relevant_content(self, text):
        """Check if content is relevant to productivity/life improvement"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

    def scrape_article_links(self, url):
        """Scrape article links from a given URL with improved selectors"""
        try:
            headers = self.get_random_headers()
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            article_links = []

            # Comprehensive selectors for different site structures
            selectors = [
                # Blog post selectors
                "article h2 a[href], article h3 a[href]",
                ".post-title a[href], .entry-title a[href]",
                ".article-title a[href], .headline a[href]",
                # List-based selectors
                ".post-list a[href], .article-list a[href]",
                ".blog-post a[href], .content-item a[href]",
                # Generic heading selectors
                "h1 a[href], h2 a[href], h3 a[href]",
                # Card-based layouts
                ".card a[href], .post-card a[href]",
                ".item a[href], .entry a[href]",
                # WordPress common selectors
                ".post a[href], .entry a[href]",
                # Fallback - any link that might be an article
                "a[href*='blog'], a[href*='article'], a[href*='post']",
            ]

            for selector in selectors:
                links = soup.select(selector)
                if links:
                    for link in links[:15]:  # Check more links
                        href = link.get("href")
                        title = link.get_text().strip()

                        if href and title and len(title) > 10:
                            # Clean up the title
                            title = re.sub(r"\s+", " ", title)
                            title = title[:200]  # Limit length

                            if self.is_relevant_content(title):
                                full_url = urljoin(url, href)

                                # Validate URL
                                parsed_url = urlparse(full_url)
                                if parsed_url.scheme in ["http", "https"]:
                                    article_data = {
                                        "title": title,
                                        "url": full_url,
                                        "source": urlparse(url).netloc,
                                        "scraped_at": datetime.now().isoformat(),
                                    }

                                    # Check if not recently recommended
                                    if not self.is_content_recent(article_data):
                                        article_links.append(article_data)

                    if article_links:
                        break  # Found articles with this selector

            return article_links[:8]  # Return more options for better randomization

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return []

    def get_youtube_videos(self, channel_url):
        """Get recent videos from a YouTube channel with improved filtering"""
        try:
            ydl_opts = {
                "quiet": True,
                "extract_flat": True,
                "playlistend": 30,  # Get more videos for better selection
                "no_warnings": True,
                "ignoreerrors": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(channel_url, download=False)

                videos = []
                if "entries" in playlist_info:
                    for entry in playlist_info["entries"]:
                        if entry and "title" in entry and "id" in entry:
                            title = entry.get("title", "")

                            if (
                                title
                                and len(title) > 5
                                and self.is_relevant_content(title)
                            ):
                                video_data = {
                                    "title": title,
                                    "url": f"https://www.youtube.com/watch?v={entry['id']}",
                                    "channel": playlist_info.get("uploader", "Unknown"),
                                    "scraped_at": datetime.now().isoformat(),
                                }

                                # Check if not recently recommended
                                if not self.is_content_recent(video_data):
                                    videos.append(video_data)

                return videos[:6]  # Return more options for randomization

        except Exception as e:
            print(f"Error getting videos from {channel_url}: {e}")
            return []

    def scrape_articles(self, count=3):
        """Scrape specified number of articles with better randomization"""
        all_articles = []
        print("🔍 Searching for productivity articles...")

        # Randomize source order
        sources = self.article_sources.copy()
        random.shuffle(sources)

        for source in sources:
            try:
                articles = self.scrape_article_links(source)
                all_articles.extend(articles)

                # Random delay between requests
                time.sleep(random.uniform(1, 3))

                if len(all_articles) >= count * 4:  # Get more for better selection
                    break

            except Exception as e:
                print(f"Error with source {source}: {e}")
                continue

        # Remove duplicates by URL
        unique_articles = []
        seen_urls = set()
        for article in all_articles:
            if article["url"] not in seen_urls:
                unique_articles.append(article)
                seen_urls.add(article["url"])

        # Randomize and return
        random.shuffle(unique_articles)
        selected_articles = unique_articles[:count]

        # Add to history
        for article in selected_articles:
            article["hash"] = self.get_content_hash(article)
            self.history["articles"].append(article)

        # Keep only last 100 articles in history
        self.history["articles"] = self.history["articles"][-100:]

        return selected_articles

    def scrape_videos(self, count=3):
        """Scrape specified number of YouTube videos with better randomization"""
        all_videos = []
        print("🎥 Searching for productivity videos...")

        # Randomize channel order
        channels = self.youtube_channels.copy()
        random.shuffle(channels)

        for channel in channels:
            try:
                videos = self.get_youtube_videos(channel)
                all_videos.extend(videos)

                # Random delay between requests
                time.sleep(random.uniform(2, 4))

                if len(all_videos) >= count * 4:  # Get more for better selection
                    break

            except Exception as e:
                print(f"Error with channel {channel}: {e}")
                continue

        # Remove duplicates by URL
        unique_videos = []
        seen_urls = set()
        for video in all_videos:
            if video["url"] not in seen_urls:
                unique_videos.append(video)
                seen_urls.add(video["url"])

        # Randomize and return
        random.shuffle(unique_videos)
        selected_videos = unique_videos[:count]

        # Add to history
        for video in selected_videos:
            video["hash"] = self.get_content_hash(video)
            self.history["videos"].append(video)

        # Keep only last 100 videos in history
        self.history["videos"] = self.history["videos"][-100:]

        return selected_videos

    def get_daily_content(self):
        """Get daily curated content bundle with guaranteed uniqueness"""
        print("🚀 Getting your daily productivity content...\n")

        # Get articles and videos
        articles = self.scrape_articles(3)
        videos = self.scrape_videos(3)

        # Update history timestamp
        self.history["last_update"] = datetime.now().isoformat()
        self.save_history()

        return articles, videos

    def display_content(self, articles, videos):
        """Display the curated content in a nice format"""
        print("=" * 70)
        print("📚 HERE IS YOUR DAILY CURATED CONTENT 📚")
        print("=" * 70)
        print()

        if articles:
            print("📖 PRODUCTIVITY ARTICLES:")
            print("-" * 35)
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article['title']}")
                print(f"   📍 Source: {article['source']}")
                print(f"   🔗 Link: {article['url']}")
                print()
        else:
            print("📖 No new articles found today. Try again later!")
            print()

        if videos:
            print("🎥 LIFE IMPROVEMENT VIDEOS:")
            print("-" * 35)
            for i, video in enumerate(videos, 1):
                print(f"{i}. {video['title']}")
                print(f"   📺 Channel: {video['channel']}")
                print(f"   🔗 Link: {video['url']}")
                print()
        else:
            print("🎥 No new videos found today. Try again later!")
            print()

        print("=" * 70)
        print("💡 Enjoy your learning journey!")
        print(
            f"📊 Content History: {len(self.history.get('articles', []))} articles, {len(self.history.get('videos', []))} videos tracked"
        )
        print("=" * 70)

    def get_recommendations_based_on_tags(self, tags, article_count=5, video_count=5):
        """
        Takes a list of tags (user preferences) and returns recommended articles and videos.
        Only include content that matches any of the tags in title, description, or tags.
        Output: 4 lists - 2 for articles (title, source, url), 2 for videos (title, channel, url)
        """
        # Lowercase tags for matching
        tags_lower = [t.lower() for t in tags if t.strip()]
        if not tags_lower:
            return [], [], [], []

        # Scrape more content for better filtering
        all_articles = []
        sources = self.article_sources.copy()
        random.shuffle(sources)
        for source in sources:
            articles = self.scrape_article_links(source)
            all_articles.extend(articles)
            if len(all_articles) >= article_count * 6:
                break

        # Filter articles by tags
        filtered_articles = []
        for article in all_articles:
            title = article.get("title", "").lower()
            # Try to get description if available (not always present)
            desc = (
                article.get("description", "").lower()
                if "description" in article
                else ""
            )
            if any(tag in title or tag in desc for tag in tags_lower):
                filtered_articles.append(article)
        # Remove duplicates and select
        seen_urls = set()
        unique_articles = []
        for a in filtered_articles:
            if a["url"] not in seen_urls:
                unique_articles.append(a)
                seen_urls.add(a["url"])
        selected_articles = unique_articles[:article_count]

        # Prepare article lists
        article_titles = [a["title"] for a in selected_articles]
        article_sources = [a["source"] for a in selected_articles]
        article_urls = [a["url"] for a in selected_articles]

        # Scrape videos
        all_videos = []
        channels = self.youtube_channels.copy()
        random.shuffle(channels)
        for channel in channels:
            videos = self.get_youtube_videos(channel)
            all_videos.extend(videos)
            if len(all_videos) >= video_count * 6:
                break

        # Filter videos by tags
        filtered_videos = []
        for video in all_videos:
            title = video.get("title", "").lower()
            # yt_dlp does not provide description/tags in flat mode, so only use title
            if any(tag in title for tag in tags_lower):
                filtered_videos.append(video)
        # Remove duplicates and select
        seen_urls = set()
        unique_videos = []
        for v in filtered_videos:
            if v["url"] not in seen_urls:
                unique_videos.append(v)
                seen_urls.add(v["url"])
        selected_videos = unique_videos[:video_count]

        # Prepare video lists
        video_titles = [v["title"] for v in selected_videos]
        video_channels = [v["channel"] for v in selected_videos]
        video_urls = [v["url"] for v in selected_videos]

        return (
            article_titles,
            article_sources,
            article_urls,
            video_titles,
            video_channels,
            video_urls,
        )


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
