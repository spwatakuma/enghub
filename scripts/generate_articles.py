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

def generate_multiple_articles(count=5):
    # Select unique genres for variety
    selected_genres = random.sample(GENRES, count) if count <= len(GENRES) else [random.choice(GENRES) for _ in range(count)]
    
    prompt = f"""
    You are an expert English teacher. 
    Your task is to generate {count} DIFFERENT reading practice articles. 
    Each article should belong to one of these genres: {selected_genres}.
    
    For EACH of the {count} topics, you must provide the content in 5 DIFFERENT difficulty levels.
    
    Level Guidelines:
    - Level 1: Beginner (CEFR A1/A2). Simple sentences, basic vocabulary. (~50 words).
    - Level 2: Pre-Intermediate (CEFR A2/B1). Daily topics, common tenses. (~100 words).
    - Level 3: Intermediate (CEFR B1/B2). Complex tenses, abstract concepts. (~150 words).
    - Level 4: Upper-Intermediate (CEFR B2/C1). Academic/professional vocabulary. (~200 words).
    - Level 5: Advanced (CEFR C1/C2). Literary vocabulary, complex structures. (~250 words).
    
    Requirements for EACH topic:
    1. The core story/information MUST be the same across all 5 levels.
    2. Provide sentence-by-sentence Japanese translations for EACH level.
    3. Provide an extensive 'vocabulary' array for EACH level (all words above that level's difficulty). Include multiple Japanese meanings for each word.
    4. Provide a detailed 'grammar' section in Japanese for EACH level, explaining structures and idioms.
    
    Output the result ONLY as a valid JSON array containing {count} objects, following this structure:
    [
      {{
        "genre": "...",
        "topic": "...",
        "levels": {{
            "1": {{
                "title": "...",
                "target_time": "1 min",
                "vocabulary": [{{"word": "...", "meaning": "..."}}],
                "grammar": "...",
                "sentences": [{{"en": "...", "ja": "..."}}]
            }},
            "2": {{ ... }}, "3": {{ ... }}, "4": {{ ... }}, "5": {{ ... }}
        }}
      }},
      ...
    ]
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 15000 # Increase token limit for large batch
        }
    }
    
    print(f"Generating {count} articles in a single API call...")
    try:
        response = requests.post(API_URL, headers=headers, json=data)
    except Exception as e:
        print(f"Request failed: {e}")
        return []
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []
        
    try:
        result = response.json()
        text = result['candidates'][0]['content']['parts'][0]['text']
        # Remove potential markdown formatting
        text = text.replace('```json', '').replace('```', '').strip()
        new_articles = json.loads(text)
        
        # Add metadata to each article
        for article in new_articles:
            article['id'] = str(uuid.uuid4())
            article['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            
        return new_articles
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return []

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
        
    # Generate 5 topics in ONE call
    new_articles = generate_multiple_articles(count=5)
        
    if new_articles:
        articles.extend(new_articles)
        # Sort by date descending
        articles.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Keep only the last 30 topics
        articles = articles[:30]
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=4)
        print(f"Successfully added {len(new_articles)} topic articles.")
    else:
        print("No articles were generated.")

if __name__ == "__main__":
    main()
