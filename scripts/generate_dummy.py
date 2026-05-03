import json
import uuid
import datetime

genres = ["Technology", "Business", "Science", "Culture", "Daily Life"]
topics = ["The Future of AI", "Remote Work Trends", "Space Exploration", "Traditional Japanese Arts", "Healthy Eating Habits"]

articles = []

for i in range(5):
    genre = genres[i]
    topic = topics[i]
    article = {
        "id": str(uuid.uuid4()),
        "date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "genre": genre,
        "topic": topic,
        "levels": {}
    }
    
    for level in range(1, 6):
        article["levels"][str(level)] = {
            "title": f"[{topic}] Level {level}",
            "target_time": f"{level} min(s)",
            "sentences": [
                {
                    "en": f"This is an English sentence for {topic} at Level {level}.",
                    "ja": f"これは{topic}のレベル{level}の日本語訳です。"
                },
                {
                    "en": f"Another sentence to practice reading at this level.",
                    "ja": f"このレベルで読む練習をするための別の文です。"
                }
            ]
        }
    articles.append(article)

with open('/home/kusanagi/enghub/DocumentRoot/data/articles.json', 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=4)
