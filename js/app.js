document.addEventListener('DOMContentLoaded', () => {
    let allArticles = [];
    let currentGenre = 'All';
    let readArticles = JSON.parse(localStorage.getItem('enghub_read_articles') || '[]');

    const articlesContainer = document.getElementById('articlesContainer');
    const template = document.getElementById('articleTemplate');

    // Fetch data
    fetch('data/articles.json?v=' + new Date().getTime())
        .then(response => {
            if (!response.ok) {
                throw new Error('Data file not found. Wait for the daily generator to create articles.');
            }
            return response.json();
        })
        .then(data => {
            // Sort by date descending
            allArticles = data.sort((a, b) => new Date(b.date) - new Date(a.date));
            renderArticles();
        })
        .catch(error => {
            console.error('Error fetching articles:', error);
            articlesContainer.innerHTML = '<div class="no-articles">No articles found. Daily generation might not have run yet.</div>';
        });

    // Genre Selector
    document.querySelectorAll('.genre-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.genre-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentGenre = e.target.dataset.genre;
            renderArticles();
        });
    });

    function renderArticles() {
        articlesContainer.innerHTML = '';
        
        const filtered = allArticles.filter(article => {
            return currentGenre === 'All' || article.genre === currentGenre;
        });

        if (filtered.length === 0) {
            articlesContainer.innerHTML = '<div class="no-articles">No articles match your selection.</div>';
            return;
        }

        filtered.forEach(article => {
            const clone = template.content.cloneNode(true);
            const articleElement = clone.querySelector('.article-card');
            
            // Set static meta
            clone.querySelector('.genre-badge').textContent = article.genre;
            clone.querySelector('.date-badge').textContent = article.date;

            // Check if read
            if (readArticles.includes(article.id)) {
                articleElement.classList.add('completed');
                clone.querySelector('.mark-read-btn').textContent = '✅ Completed';
            }

            // Handle local level buttons
            const levelBtns = clone.querySelectorAll('.local-level-btn');
            levelBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    levelBtns.forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    const level = e.target.dataset.level;
                    renderArticleLevel(articleElement, article, level);
                });
            });

            // Toggle all translations
            const toggleAllBtn = clone.querySelector('.toggle-all-btn');
            toggleAllBtn.addEventListener('click', (e) => {
                const card = e.target.closest('.article-card');
                const jaElements = card.querySelectorAll('.sentence-ja');
                const anyHidden = Array.from(jaElements).some(el => !el.classList.contains('show'));
                
                jaElements.forEach(el => {
                    if (anyHidden) {
                        el.classList.add('show');
                    } else {
                        el.classList.remove('show');
                    }
                });
                
                toggleAllBtn.textContent = anyHidden ? 'Hide All Translations' : 'Toggle All Translations';
            });

            // Mark as Read
            const markReadBtn = clone.querySelector('.mark-read-btn');
            markReadBtn.addEventListener('click', () => {
                if (!readArticles.includes(article.id)) {
                    readArticles.push(article.id);
                    localStorage.setItem('enghub_read_articles', JSON.stringify(readArticles));
                    articleElement.classList.add('completed');
                    markReadBtn.textContent = '✅ Completed';
                }
            });

            // Initial render (Level 1)
            renderArticleLevel(articleElement, article, '1');
            
            articlesContainer.appendChild(clone);
        });
    }

    function renderArticleLevel(articleElement, articleData, levelStr) {
        const levelData = articleData.levels[levelStr];
        if (!levelData) return;

        articleElement.querySelector('.time-badge').textContent = `Target: ${levelData.target_time}`;
        articleElement.querySelector('.article-title').textContent = levelData.title;

        // Render Vocabulary if it exists
        const vocabSection = articleElement.querySelector('.vocabulary-section');
        const vocabList = articleElement.querySelector('.vocab-list');
        if (levelData.vocabulary && levelData.vocabulary.length > 0) {
            vocabList.innerHTML = '';
            levelData.vocabulary.forEach(v => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="vocab-word">${v.word}</span> - ${v.meaning}`;
                vocabList.appendChild(li);
            });
            vocabSection.style.display = 'block';
        } else {
            vocabSection.style.display = 'none';
        }

        const contentDiv = articleElement.querySelector('.article-content');
        contentDiv.innerHTML = ''; // Clear previous sentences
        
        levelData.sentences.forEach(sentence => {
            const block = document.createElement('div');
            block.className = 'sentence-block';
            
            // TTS Button
            const ttsBtn = document.createElement('button');
            ttsBtn.className = 'tts-btn';
            ttsBtn.innerHTML = '🔊';
            ttsBtn.title = 'Read Aloud';
            ttsBtn.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent toggling translation
                speakText(sentence.en);
            });

            const enP = document.createElement('p');
            enP.className = 'sentence-en';
            enP.appendChild(ttsBtn);
            enP.appendChild(document.createTextNode(sentence.en));
            
            const jaP = document.createElement('p');
            jaP.className = 'sentence-ja';
            jaP.textContent = sentence.ja;

            // Click to toggle
            enP.addEventListener('click', () => {
                jaP.classList.toggle('show');
            });

            block.appendChild(enP);
            block.appendChild(jaP);
            contentDiv.appendChild(block);
        });

        const toggleAllBtn = articleElement.querySelector('.toggle-all-btn');
        if (toggleAllBtn) {
            toggleAllBtn.textContent = 'Toggle All Translations';
        }
    }

    function speakText(text) {
        if (!('speechSynthesis' in window)) {
            alert('Your browser does not support text-to-speech.');
            return;
        }
        speechSynthesis.cancel(); // Stop current speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 0.9; // Slightly slower for learning
        speechSynthesis.speak(utterance);
    }
});
