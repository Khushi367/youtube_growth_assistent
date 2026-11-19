"""
recommendation.py
------------------
Rule-based NLP helpers that generate:
  - Title suggestions
  - Description + hashtag suggestions
  - Best upload time recommendation (per category, learned from data/youtube_data.csv)
  - Thumbnail improvement tips
  - Basic audience-engagement analysis text

These are deterministic NLP/template-based generators (no external LLM API calls),
so the app works fully offline once trained.
"""

import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "youtube_data.csv")

# ---------------------------------------------------------------------------
# Title suggestion templates (NLP rule-based generation)
# ---------------------------------------------------------------------------
TITLE_TEMPLATES = [
    "How {topic} Can Transform Your {category} Game in 2026",
    "{n} {topic} Secrets Nobody Tells You About",
    "I Tried {topic} for 30 Days — Here's What Happened",
    "The Ultimate {topic} Guide for {category} Creators",
    "Why Everyone Is Talking About {topic} Right Now",
    "{topic}: What I Wish I Knew Before Starting",
    "Stop Doing {topic} Wrong — Do THIS Instead",
    "{n} {topic} Mistakes Killing Your {category} Channel",
    "{topic} Explained in {n} Minutes",
    "This {topic} Trick Changed My {category} Results",
]

DESCRIPTION_TEMPLATE = """In this video, we dive deep into {topic} and how it relates to {category}. \
You'll learn practical, actionable steps you can use right away, common mistakes to avoid, \
and insider tips that most creators overlook. Whether you're a beginner or already experienced \
in {category}, this video is packed with value.

⏱️ Timestamps and key takeaways are in the pinned comment.
👍 If this helped you, drop a like and subscribe for more {category} content.
💬 Let us know in the comments what you'd like covered next!

{hashtags}
"""

HASHTAG_POOL_BY_CATEGORY = {
    "Tech": ["#Tech", "#TechTips", "#Innovation", "#Gadgets", "#TechReview"],
    "Gaming": ["#Gaming", "#Gamer", "#GamingCommunity", "#LetsPlay", "#GameOn"],
    "Vlog": ["#Vlog", "#DailyVlog", "#LifeUpdate", "#VlogLife", "#BehindTheScenes"],
    "Education": ["#Education", "#LearnOnYouTube", "#StudyTips", "#Explained", "#HowTo"],
    "Comedy": ["#Comedy", "#Funny", "#Humor", "#Sketch", "#LOL"],
    "Music": ["#Music", "#NewMusic", "#MusicVideo", "#Cover", "#Artist"],
    "Fitness": ["#Fitness", "#Workout", "#FitnessMotivation", "#HealthyLifestyle", "#GymLife"],
    "Cooking": ["#Cooking", "#Recipe", "#FoodieLife", "#HomeCooking", "#Foodgasm"],
    "Finance": ["#Finance", "#PersonalFinance", "#MoneyTips", "#Investing", "#FinancialFreedom"],
    "Beauty": ["#Beauty", "#Makeup", "#Skincare", "#BeautyTips", "#GRWM"],
}
GENERIC_HASHTAGS = ["#YouTube", "#Trending", "#Viral", "#MustWatch", "#ContentCreator"]

THUMBNAIL_TIPS = [
    "Use large, bold, high-contrast text (max 4-6 words) so it's readable at small sizes.",
    "Include an expressive human face with clear emotion — it boosts click-through rate.",
    "Stick to 2-3 dominant colors and keep the background simple and uncluttered.",
    "Avoid replicating your title exactly in the thumbnail — make it complementary, not redundant.",
    "Use a bright accent color (red, yellow, orange) to make the thumbnail pop in the feed.",
    "Add directional cues (arrows, circles) to draw the eye to the key element.",
    "Keep important elements away from the edges — corners get cropped on mobile.",
    "A/B test 2-3 thumbnail variants using YouTube Studio's testing feature.",
    "Ensure text and subject are readable even at 120x90px (mobile feed size).",
    "Maintain a consistent visual branding style (fonts/colors) across videos for channel recognition.",
]

ENGAGEMENT_TIPS = {
    "low_ctr": "Your CTR is below average. Try more curiosity-driven titles and higher-contrast thumbnails.",
    "low_engagement": "Engagement rate (likes+comments+shares / views) is low. Ask a direct question in the video and pin a comment to spark replies.",
    "low_watch_ratio": "Viewers are dropping off early relative to video length. Tighten your intro (first 15 seconds) and remove slow segments.",
    "good": "Your metrics look strong! Keep the current format/style and consider doubling down on this topic as a series.",
}


def _clean_topic(topic: str) -> str:
    topic = re.sub(r"[^A-Za-z0-9 ]+", "", topic).strip()
    return topic if topic else "Content Growth"


def generate_title_suggestions(topic: str, category: str, n_suggestions: int = 5) -> list:
    topic = _clean_topic(topic)
    import random
    random.seed(hash(topic + category) % (2**32))
    templates = random.sample(TITLE_TEMPLATES, min(n_suggestions, len(TITLE_TEMPLATES)))
    numbers = [5, 7, 10, 3, 9]
    suggestions = []
    for i, tmpl in enumerate(templates):
        suggestions.append(tmpl.format(topic=topic, category=category, n=numbers[i % len(numbers)]))
    return suggestions


def generate_hashtags(topic: str, category: str, n_tags: int = 8) -> list:
    topic_tag = "#" + re.sub(r"[^A-Za-z0-9]", "", topic).strip()
    cat_tags = HASHTAG_POOL_BY_CATEGORY.get(category, [])
    tags = [t for t in ([topic_tag] + cat_tags + GENERIC_HASHTAGS) if len(t) > 1]
    seen = []
    for t in tags:
        if t.lower() not in [s.lower() for s in seen]:
            seen.append(t)
    return seen[:n_tags]


def generate_description(topic: str, category: str) -> str:
    topic = _clean_topic(topic)
    hashtags = " ".join(generate_hashtags(topic, category))
    return DESCRIPTION_TEMPLATE.format(topic=topic, category=category, hashtags=hashtags)


def best_upload_time(category: str) -> dict:
    """
    Looks at historical data/youtube_data.csv, and returns the upload hour(s) that
    historically correlate with High growth for the given category. Falls back to
    general best-practice hours if the category has too little data.
    """
    fallback = {"best_hour": 18, "window": "6:00 PM - 9:00 PM (viewer local time)",
                "note": "General best practice: weekday evenings and weekend late mornings "
                        "tend to see the most viewer activity."}
    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        return fallback

    subset = df[df["category"] == category]
    if len(subset) < 15:
        return fallback

    high_growth = subset[subset["growth_label"] == "High"]
    if high_growth.empty:
        return fallback

    best_hour = int(high_growth["upload_hour"].mode()[0])
    start = best_hour
    end = (best_hour + 2) % 24

    def fmt(h):
        suffix = "AM" if h < 12 else "PM"
        h12 = h % 12
        h12 = 12 if h12 == 0 else h12
        return f"{h12}:00 {suffix}"

    return {
        "best_hour": best_hour,
        "window": f"{fmt(start)} - {fmt(end)}",
        "note": f"Based on {len(high_growth)} historically high-growth {category} videos in the dataset.",
    }


def thumbnail_suggestions(n: int = 5) -> list:
    import random
    return random.sample(THUMBNAIL_TIPS, min(n, len(THUMBNAIL_TIPS)))


def analyze_engagement(views: int, likes: int, comments: int, shares: int,
                        ctr_percent: float, watch_time_sec: float, duration_sec: int) -> dict:
    engagement_rate = (likes + comments + shares) / max(views, 1) * 100
    watch_ratio = watch_time_sec / max(duration_sec, 1) * 100

    flags = []
    if ctr_percent < 4:
        flags.append(ENGAGEMENT_TIPS["low_ctr"])
    if engagement_rate < 3:
        flags.append(ENGAGEMENT_TIPS["low_engagement"])
    if watch_ratio < 35:
        flags.append(ENGAGEMENT_TIPS["low_watch_ratio"])
    if not flags:
        flags.append(ENGAGEMENT_TIPS["good"])

    return {
        "engagement_rate_percent": round(engagement_rate, 2),
        "watch_ratio_percent": round(watch_ratio, 2),
        "ctr_percent": ctr_percent,
        "tips": flags,
    }
