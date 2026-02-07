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
    totalPages: 1
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
});

async function initializeApp() {
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
    const data = await fetchAPI('/api/categories');

    if (data && data.success) {
        state.categories = data.data.categories;
        renderCategories();
    }
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
            <label for="cat-${cat.id}">${cat.icon} ${cat.name} (${cat.article_count})</label>
        </div>
    `).join('');
}

// Load Sources
async function loadSources() {
    const data = await fetchAPI('/api/sources');

    if (data && data.success) {
        state.sources = data.data.sources;
        renderSources();
    }
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
    const data = await fetchAPI('/api/trending?days=7&limit=10');

    if (data && data.success) {
        state.trending = data.data.trending_topics;
        renderTrending();
    }
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

    // Build query parameters
    const params = new URLSearchParams({
        page: state.currentPage,
        limit: 12
    });

    // Add filters
    if (state.selectedCategories.length > 0) {
        params.append('category', state.selectedCategories[0]); // API supports one category
    }

    if (state.selectedSources.length > 0) {
        params.append('source', state.selectedSources[0]); // API supports one source
    }

    // Handle search differently
    let endpoint;
    if (state.searchQuery) {
        endpoint = `/api/search?q=${encodeURIComponent(state.searchQuery)}&limit=50`;
    } else {
        endpoint = `/api/articles?${params.toString()}`;
    }

    const data = await fetchAPI(endpoint);

    if (data && data.success) {
        if (state.searchQuery) {
            state.articles = data.data.results;
            state.totalPages = 1; // Search doesn't paginate
        } else {
            state.articles = data.data.articles;
            state.totalPages = data.data.total_pages;
        }

        renderArticles();
        renderPagination();
        updateResultsCount();
    } else {
        showError();
    }
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

    return `
        <article class="article-card" onclick="openArticle('${article.url}')">
            ${imageHtml}
            <div class="article-content">
                <div class="article-meta">
                    <span class="source-badge">${article.source}</span>
                    <span class="article-date">${date}</span>
                </div>
                <h2 class="article-title">${article.title}</h2>
                ${summaryHtml}
                ${categoriesHtml}
                <div class="article-footer">
                    <a href="${article.url}" target="_blank" class="read-more" onclick="event.stopPropagation()">
                        Read Full Article →
                    </a>
                </div>
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
