// Robotics Daily Report - Main JavaScript

// API Base URL - update for production
const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:5000' : '';

// State Management
const state = {
    currentPage: 1,
    selectedCategories: [],
    selectedSources: [],
    searchQuery: '',
    articles: [],
    categories: [],
    sources: [],
    trending: [],
    totalPages: 1,
    allArticles: [],  // Store all articles for client-side filtering
    allData: null    // Store the entire dataset
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function loadDataFile() {
    /**Load the static data.json file */
    try {
        const response = await fetch('/data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        state.allData = await response.json();
        state.allArticles = state.allData.articles || [];
        return true;
    } catch (error) {
        console.error('Error loading data file:', error);
        return false;
    }
}

async function initializeApp() {
    // Load the data file first
    const loaded = await loadDataFile();
    if (!loaded) {
        showError();
        return;
    }

    // Load UI components
    await Promise.all([
        loadCategories(),
        loadSources(),
        loadTrending()
    ]);

    await loadArticles();
}

// Event Listeners
function setupEventListeners() {
    // Search
    document.getElementById('searchBtn').addEventListener('click', handleSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    // Clear Filters
    document.getElementById('clearFilters').addEventListener('click', clearFilters);

    // Modal event listeners
    setupModalListeners();
}

function setupModalListeners() {
    // Close modal on backdrop click
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
        backdrop.addEventListener('click', () => {
            closeArticleModal();
            closeBriefModal();
        });
    });

    // Close modal on X click
    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            closeArticleModal();
            closeBriefModal();
        });
    });

    // Read brief option
    document.getElementById('readBrief').addEventListener('click', openBriefView);

    // Visit original option
    document.getElementById('visitOriginal').addEventListener('click', () => {
        if (selectedArticle) {
            window.open(selectedArticle.url, '_blank');
            closeArticleModal();
        }
    });

    // Brief modal buttons
    document.getElementById('visitFromBrief').addEventListener('click', visitOriginalFromBrief);
    document.getElementById('closeBrief').addEventListener('click', closeBriefModal);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeArticleModal();
            closeBriefModal();
        }
    });
}

// API Calls
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

// Load Categories
async function loadCategories() {
    if (!state.allData) return;

    state.categories = state.allData.categories || [];

    // Count articles per category
    for (const cat of state.categories) {
        cat.article_count = state.allArticles.filter(a =>
            (a.categories || []).includes(cat.name)
        ).length;
    }

    renderCategories();
}

function renderCategories() {
    const container = document.getElementById('categoryFilters');

    if (state.categories.length === 0) {
        container.innerHTML = '<p class="filter-loading">No categories available</p>';
        return;
    }

    container.innerHTML = state.categories.map(cat => `
        <div class="filter-item">
            <input type="checkbox"
                   id="cat-${cat.id}"
                   value="${cat.name}"
                   onchange="toggleCategory('${cat.name}')">
            <label for="cat-${cat.id}">${cat.name}</label>
        </div>
    `).join('');
}

// Load Sources
async function loadSources() {
    if (!state.allData) return;

    state.sources = state.allData.sources || [];
    renderSources();
}

function renderSources() {
    const container = document.getElementById('sourceFilters');

    if (state.sources.length === 0) {
        container.innerHTML = '<p class="filter-loading">No sources available</p>';
        return;
    }

    container.innerHTML = state.sources.map((source, idx) => `
        <div class="filter-item">
            <input type="checkbox"
                   id="source-${idx}"
                   value="${source.source}"
                   onchange="toggleSource('${source.source}')">
            <label for="source-${idx}">${source.source} (${source.article_count})</label>
        </div>
    `).join('');
}

// Load Trending
async function loadTrending() {
    if (!state.allData) return;

    state.trending = (state.allData.trending || []).slice(0, 10);
    renderTrending();
}

function renderTrending() {
    const container = document.getElementById('trendingTopics');

    if (state.trending.length === 0) {
        container.innerHTML = '<p class="filter-loading">No trending topics yet</p>';
        return;
    }

    container.innerHTML = state.trending.map(topic => `
        <div class="trending-item" onclick="searchTopic('${topic.topic_name}')">
            <div class="trending-name">${topic.topic_name}</div>
            <div class="trending-count">${topic.mention_count} mention${topic.mention_count > 1 ? 's' : ''}</div>
        </div>
    `).join('');
}

// Load Articles
async function loadArticles() {
    showLoading();

    if (!state.allArticles || state.allArticles.length === 0) {
        showError();
        return;
    }

    // Client-side filtering
    let filtered = [...state.allArticles];

    // Filter by category
    if (state.selectedCategories.length > 0) {
        filtered = filtered.filter(article =>
            state.selectedCategories.some(cat => (article.categories || []).includes(cat))
        );
    }

    // Filter by source
    if (state.selectedSources.length > 0) {
        filtered = filtered.filter(article =>
            state.selectedSources.includes(article.source)
        );
    }

    // Search
    if (state.searchQuery) {
        const query = state.searchQuery.toLowerCase();
        filtered = filtered.filter(article => {
            const title = (article.title || '').toLowerCase();
            const summary = (article.summary || '').toLowerCase();
            const excerpt = (article.excerpt || '').toLowerCase();
            return title.includes(query) || summary.includes(query) || excerpt.includes(query);
        });
    }

    // Paginate
    const limit = 12;
    state.totalPages = Math.max(1, Math.ceil(filtered.length / limit));
    const start = (state.currentPage - 1) * limit;
    const end = start + limit;
    state.articles = filtered.slice(start, end);

    renderArticles();
    renderPagination();
    updateResultsCount();
}

function renderArticles() {
    const container = document.getElementById('articlesGrid');

    if (state.articles.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <h2>No articles found</h2>
                <p>Try adjusting your filters or search query</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.articles.map(article => createArticleCard(article)).join('');
}

// Store currently selected article
let selectedArticle = null;

function createArticleCard(article) {
    const date = article.published_date ?
        new Date(article.published_date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        }) : 'Recent';

    const imageHtml = article.image_url ?
        `<img src="${article.image_url}" alt="${article.title}" class="article-image" onerror="this.style.display='none'">` :
        '';

    const categoriesHtml = article.categories && article.categories.length > 0 ?
        `<div class="article-categories">
            ${article.categories.map(cat => `<span class="category-tag">${cat}</span>`).join('')}
        </div>` : '';

    const summaryHtml = article.summary ?
        `<p class="article-summary">${article.summary}</p>` :
        (article.excerpt ? `<p class="article-summary">${truncate(article.excerpt, 200)}</p>` : '');

    // Create a unique ID for the article
    const articleId = article.id || article.url;

    return `
        <article class="article-card" data-article-id="${articleId}" onclick="openArticleModal(${articleId})">
            ${imageHtml}
            <div class="article-content">
                <div class="article-meta">
                    <span class="source-badge">${article.source}</span>
                    <span class="article-date">${date}</span>
                </div>
                <h2 class="article-title">${article.title}</h2>
                ${summaryHtml}
                ${categoriesHtml}
            </div>
        </article>
    `;
}

function renderPagination() {
    const container = document.getElementById('pagination');

    if (state.totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let paginationHTML = '';

    // Previous button
    paginationHTML += `
        <button class="pagination-btn"
                onclick="changePage(${state.currentPage - 1})"
                ${state.currentPage === 1 ? 'disabled' : ''}>
            ← Previous
        </button>
    `;

    // Page numbers
    for (let i = 1; i <= Math.min(state.totalPages, 5); i++) {
        const page = i === 5 && state.totalPages > 5 ? state.totalPages : i;
        paginationHTML += `
            <button class="pagination-btn ${page === state.currentPage ? 'active' : ''}"
                    onclick="changePage(${page})">
                ${page}
            </button>
        `;
    }

    // Next button
    paginationHTML += `
        <button class="pagination-btn"
                onclick="changePage(${state.currentPage + 1})"
                ${state.currentPage === state.totalPages ? 'disabled' : ''}>
            Next →
        </button>
    `;

    container.innerHTML = paginationHTML;
}

// Filter Functions
function toggleCategory(category) {
    const index = state.selectedCategories.indexOf(category);

    if (index > -1) {
        state.selectedCategories.splice(index, 1);
    } else {
        state.selectedCategories = [category]; // Single category for now
    }

    state.currentPage = 1;
    loadArticles();
}

function toggleSource(source) {
    const index = state.selectedSources.indexOf(source);

    if (index > -1) {
        state.selectedSources.splice(index, 1);
    } else {
        state.selectedSources = [source]; // Single source for now
    }

    state.currentPage = 1;
    loadArticles();
}

function clearFilters() {
    state.selectedCategories = [];
    state.selectedSources = [];
    state.searchQuery = '';
    state.currentPage = 1;

    // Uncheck all checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.getElementById('searchInput').value = '';

    loadArticles();
}

// Search Functions
function handleSearch() {
    const input = document.getElementById('searchInput');
    state.searchQuery = input.value.trim();
    state.currentPage = 1;

    if (state.searchQuery) {
        loadArticles();
    }
}

function searchTopic(topic) {
    document.getElementById('searchInput').value = topic;
    handleSearch();
}

// Pagination
function changePage(page) {
    if (page < 1 || page > state.totalPages) return;

    state.currentPage = page;
    loadArticles();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Helper Functions
function updateResultsCount() {
    const count = state.articles.length;
    const text = state.searchQuery ?
        `Found ${count} results for "${state.searchQuery}"` :
        `Showing ${count} articles`;

    document.getElementById('resultsCount').textContent = text;
}

function showLoading() {
    document.getElementById('articlesGrid').innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Loading robotics news...</p>
        </div>
    `;
}

function showError() {
    document.getElementById('articlesGrid').innerHTML = `
        <div class="no-results">
            <h2>Error loading articles</h2>
            <p>Please try again later</p>
        </div>
    `;
}

function truncate(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substr(0, maxLength).trim() + '...';
}

function openArticle(url) {
    window.open(url, '_blank');
}

// Modal handling
function openArticleModal(articleId) {
    // Find the article from state
    selectedArticle = state.allArticles.find(a => a.id === articleId);

    if (!selectedArticle) return;

    // Show modal
    document.getElementById('articleModal').classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeArticleModal() {
    document.getElementById('articleModal').classList.remove('active');
    document.body.style.overflow = 'auto';
}

function openBriefView() {
    if (!selectedArticle) return;

    // Build brief content
    const categories = selectedArticle.categories && selectedArticle.categories.length > 0
        ? `<div class="category-list">
            ${selectedArticle.categories.map(cat => `<span class="category-item">${cat}</span>`).join('')}
        </div>`
        : '';

    const summary = selectedArticle.summary || 'No AI-generated summary available for this article.';

    const briefHTML = `
        <h2 class="modal-title">${selectedArticle.title}</h2>
        <div class="brief-meta">
            <span>${selectedArticle.source}</span>
            <span>•</span>
            <span>${formatDate(selectedArticle.published_date)}</span>
        </div>
        ${categories}
        <div class="brief-summary">
            <h3>AI-Generated Brief</h3>
            <p>${summary}</p>
        </div>
        ${selectedArticle.excerpt ? `
            <h3>Article Preview</h3>
            <p>${truncate(stripHTML(selectedArticle.excerpt), 400)}</p>
        ` : ''}
    `;

    document.getElementById('briefContent').innerHTML = briefHTML;

    // Close article modal and open brief modal
    closeArticleModal();
    document.getElementById('briefModal').classList.add('active');
}

function closeBriefModal() {
    document.getElementById('briefModal').classList.remove('active');
    document.body.style.overflow = 'auto';
}

function visitOriginalFromBrief() {
    if (selectedArticle) {
        window.open(selectedArticle.url, '_blank');
        closeBriefModal();
    }
}

function formatDate(dateString) {
    if (!dateString) return 'Recent';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function stripHTML(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
}

