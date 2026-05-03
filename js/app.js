document.addEventListener('DOMContentLoaded', () => {
    let allArticles = [];
    let currentLevel = 1;
    let currentGenre = 'All';

    const articlesContainer = document.getElementById('articlesContainer');
    const template = document.getElementById('articleTemplate');

    // Fetch data
    fetch('data/articles.json')
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

    // Level Selector
    document.querySelectorAll('.level-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.level-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentLevel = parseInt(e.target.dataset.level);
            renderArticles();
        });
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
            const matchLevel = article.level === currentLevel;
            const matchGenre = currentGenre === 'All' || article.genre === currentGenre;
            return matchLevel && matchGenre;
        });

        if (filtered.length === 0) {
            articlesContainer.innerHTML = '<div class="no-articles">No articles match your selection.</div>';
            return;
        }

        filtered.forEach(article => {
            const clone = template.content.cloneNode(true);
            
            clone.querySelector('.level-badge').textContent = `Level ${article.level}`;
            clone.querySelector('.genre-badge').textContent = article.genre;
            clone.querySelector('.date-badge').textContent = article.date;
            clone.querySelector('.time-badge').textContent = `Target: ${article.target_time}`;
            clone.querySelector('.article-title').textContent = article.title;

            const contentDiv = clone.querySelector('.article-content');
            
            article.sentences.forEach(sentence => {
                const block = document.createElement('div');
                block.className = 'sentence-block';
                
                const enP = document.createElement('p');
                enP.className = 'sentence-en';
                enP.textContent = sentence.en;
                
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

            // Toggle all button
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

            articlesContainer.appendChild(clone);
        });
    }
});
