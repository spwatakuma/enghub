import os
import json
import random
import datetime
import requests
import time
import uuid

# User provided key as fallback
API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyCELNp_EiJu4fDlt_Np68TY6KbMLw4Y1e8')
MODEL = 'gemini-2.5-flash'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

GENRES = ["Technology", "Business", "Science", "Culture", "Daily Life"]

def generate_topic_article(genre):
    prompt = f"""
    You are an expert English teacher. 
    Choose a specific, interesting, and random topic within the genre: {genre}.
    Write a reading practice article about this topic in 5 DIFFERENT difficulty levels.
    
    Level Guidelines:
    - Level 1: Beginner (CEFR A1/A2). Simple sentences, basic vocabulary, mostly present and simple past tense. (~50 words). Target time: "1 min"
    - Level 2: Pre-Intermediate (CEFR A2/B1). Daily topics, comparatives, some future and continuous tenses. (~100 words). Target time: "2 mins"
    - Level 3: Intermediate (CEFR B1/B2). Perfect tenses, passive voice, relative pronouns, more abstract concepts. (~150 words). Target time: "3 mins"
    - Level 4: Upper-Intermediate (CEFR B2/C1). Complex sentences, academic/professional vocabulary, nuanced meanings. (~200 words). Target time: "4 mins"
    - Level 5: Advanced (CEFR C1/C2). Highly academic or literary vocabulary, complex grammatical structures, idioms. (~250 words). Target time: "5 mins"
    
    Requirements:
    1. The core story or information MUST be the same across all 5 levels, just written differently according to the difficulty.
    2. Provide sentence-by-sentence Japanese translations for EACH level.
    3. For EACH level, provide an extensive 'vocabulary' array. Include ALL words that are difficult for that specific level. 
       - For Level 1, include words above A1.
       - For Level 3, include words above B1.
       - For EACH word, if there are multiple ways to translate it, provide all common Japanese meanings separated by commas (e.g., "influence": "影響、感化、左右する").
    4. For EACH level, provide a 'grammar' section at the end. This should be a detailed explanation (in Japanese) of the important grammatical structures, idioms, or specific expressions used in that level's text. This can be as long as needed to be helpful for a student.
    5. Output the result ONLY as a valid JSON object with the following structure (no markdown formatting blocks, just the raw JSON):
    {{
        "genre": "{genre}",
        "topic": "The chosen topic's name in English",
        "levels": {{
            "1": {{
                "title": "Title for level 1",
                "target_time": "1 min",
                "vocabulary": [
                    {{"word": "word1", "meaning": "meaning1, meaning2"}},
                    {{"word": "word2", "meaning": "meaning3"}}
                ],
                "grammar": "Detailed explanation of grammar in Japanese...",
                "sentences": [
                    {{"en": "English sentence 1.", "ja": "Japanese translation 1."}}
                ]
            }},
            "2": {{ "title": "...", "target_time": "...", "vocabulary": [], "grammar": "...", "sentences": [] }},
            "3": {{ "title": "...", "target_time": "...", "vocabulary": [], "grammar": "...", "sentences": [] }},
            "4": {{ "title": "...", "target_time": "...", "vocabulary": [], "grammar": "...", "sentences": [] }},
            "5": {{ "title": "...", "target_time": "...", "vocabulary": [], "grammar": "...", "sentences": [] }}
        }}
    }}
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }
    
    print(f"Generating Topic Article for genre: {genre}...")
    try:
        response = requests.post(API_URL, headers=headers, json=data)
    except Exception as e:
        print(f"Request failed: {e}")
        return None
    
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
        # Add metadata
        article['id'] = str(uuid.uuid4())
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
    
    # Generate 5 topics
    # Note: Free tier limits are usually around 15 RPM (Requests Per Minute)
    # and 1500 RPD (Requests Per Day). We generate 5 topics once a day.
    # We use a 10s delay to be safe and avoid bursts.
    for _ in range(5):
        genre = random.choice(GENRES)
        article = generate_topic_article(genre)
        if article:
            new_articles.append(article)
        time.sleep(10) # Safe delay for free tier
        
    if new_articles:
        articles.extend(new_articles)
        # Sort by date descending
        articles.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Keep only the last 30 topics to manage file size
        articles = articles[:30]
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print(f"Successfully added {len(new_articles)} topic articles.")
    else:
        print("No articles were generated.")

if __name__ == "__main__":
    main()
