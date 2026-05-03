import os
import json
import random
import datetime
import requests
import time

# User provided key as fallback
API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCELNp_EiJu4fDlt_Np68TY6KbMLw4Y1e8')
MODEL = 'gemini-2.5-flash'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

GENRES = ["Technology", "Business", "Science", "Culture", "Daily Life"]

LEVEL_GUIDELINES = {
    1: {"cefr": "A1/A2", "desc": "Beginner. Simple sentences, basic vocabulary, mostly present and simple past tense.", "time": "1 min"},
    2: {"cefr": "A2/B1", "desc": "Pre-Intermediate. Daily topics, comparatives, some future and continuous tenses.", "time": "2 mins"},
    3: {"cefr": "B1/B2", "desc": "Intermediate. Perfect tenses, passive voice, relative pronouns, more abstract concepts.", "time": "3 mins"},
    4: {"cefr": "B2/C1", "desc": "Upper-Intermediate. Complex sentences, academic/professional vocabulary, nuanced meanings.", "time": "4 mins"},
    5: {"cefr": "C1/C2", "desc": "Advanced. Highly academic or literary vocabulary, complex grammatical structures, idioms.", "time": "5 mins"}
}

def generate_article(level, genre):
    guide = LEVEL_GUIDELINES[level]
    prompt = f"""
    You are an expert English teacher. Create an English reading practice article for Level {level} ({guide['cefr']}).
    Genre/Topic: {genre}
    Guidelines: {guide['desc']}
    
    Requirements:
    1. The article should be interesting and informative.
    2. Length should be appropriate for the level (Level 1: ~50 words, Level 5: ~250 words).
    3. Output the result ONLY as a valid JSON object with the following structure (no markdown formatting blocks, just the raw JSON):
    {{
        "title": "Article Title",
        "level": {level},
        "genre": "{genre}",
        "target_time": "{guide['time']}",
        "sentences": [
            {{"en": "English sentence 1.", "ja": "Japanese translation 1."}},
            {{"en": "English sentence 2.", "ja": "Japanese translation 2."}}
        ]
    }}
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }
    
    print(f"Generating Level {level} article ({genre})...")
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
        
    try:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        # Remove potential markdown formatting
        text = text.replace('```json', '').replace('```', '').strip()
        article = json.loads(text)
        # Add generation date
        article['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        return article
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return None

def main():
    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'articles.json')
    
    # Load existing articles
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            try:
                articles = json.load(f)
            except:
                articles = []
    else:
        articles = []
        
    new_articles = []
    
    # Generate one article for each level
    for level in range(1, 6):
        genre = random.choice(GENRES)
        article = generate_article(level, genre)
        if article:
            new_articles.append(article)
        time.sleep(2) # Prevent rate limiting
        
    if new_articles:
        articles.extend(new_articles)
        # Sort by date descending
        articles.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print(f"Successfully added {len(new_articles)} articles.")
    else:
        print("No articles were generated.")

if __name__ == "__main__":
    main()
