from flask import Flask, render_template_string, request, jsonify
import logging
from Backend.web_crawler import WikipediaCrawler
from Backend.pagerank import PageRank
from Backend.indexer import BM25Indexer
from Backend.ranker import SearchRanker
from Backend.config import WEB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for search components
ranker = None
pages_data = None

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PageRank Search Engine</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
            padding-top: 40px;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .search-box {
            background: white;
            border-radius: 50px;
            padding: 10px 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .search-box input {
            flex: 1;
            border: none;
            outline: none;
            font-size: 1.1em;
            padding: 15px;
            background: transparent;
        }
        
        .search-box button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 35px;
            border-radius: 25px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .search-box button:hover {
            transform: scale(1.05);
        }
        
        .search-box button:active {
            transform: scale(0.95);
        }
        
        .sample-queries {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .sample-queries p {
            color: white;
            margin-bottom: 10px;
            opacity: 0.9;
        }
        
        .sample-queries .query-chip {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            cursor: pointer;
            transition: background 0.3s;
            font-size: 0.9em;
        }
        
        .sample-queries .query-chip:hover {
            background: rgba(255,255,255,0.3);
        }
        
        .results {
            display: none;
        }
        
        .results.show {
            display: block;
        }
        
        .result-item {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .result-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        
        .result-item h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        
        .result-item .summary {
            color: #555;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .result-item .metadata {
            display: flex;
            gap: 20px;
            font-size: 0.9em;
            color: #888;
        }
        
        .result-item .score-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .result-item .link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .result-item .link:hover {
            text-decoration: underline;
        }
        
        .loading {
            text-align: center;
            color: white;
            font-size: 1.2em;
            display: none;
        }
        
        .loading.show {
            display: block;
        }
        
        .no-results {
            text-align: center;
            color: white;
            font-size: 1.2em;
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 15px;
            display: none;
        }
        
        .no-results.show {
            display: block;
        }
        
        .stats {
            text-align: center;
            color: white;
            margin-bottom: 20px;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 PageRank Search</h1>
            <p>Intelligent search powered by PageRank + BM25</p>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Enter your search query..." 
                   onkeypress="handleKeyPress(event)">
            <button onclick="search()">Search</button>
        </div>
        
        <div class="sample-queries">
            <p>Try these queries:</p>
            <span class="query-chip" onclick="searchSample('machine learning')">machine learning</span>
            <span class="query-chip" onclick="searchSample('artificial intelligence')">artificial intelligence</span>
            <span class="query-chip" onclick="searchSample('graph algorithms')">graph algorithms</span>
            <span class="query-chip" onclick="searchSample('neural networks')">neural networks</span>
            <span class="query-chip" onclick="searchSample('database systems')">database systems</span>
        </div>
        
        <div class="loading" id="loading">
            Searching...
        </div>
        
        <div class="stats" id="stats"></div>
        
        <div class="results" id="results"></div>
        
        <div class="no-results" id="noResults">
            No results found. Try a different query.
        </div>
    </div>
    
    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                search();
            }
        }
        
        function searchSample(query) {
            document.getElementById('searchInput').value = query;
            search();
        }
        
        function search() {
            const query = document.getElementById('searchInput').value.trim();
            
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            // Show loading, hide results
            document.getElementById('loading').classList.add('show');
            document.getElementById('results').classList.remove('show');
            document.getElementById('noResults').classList.remove('show');
            document.getElementById('stats').textContent = '';
            
            // Make API request
            fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('loading').classList.remove('show');
                alert('Search error. Please try again.');
            });
        }
        
        function displayResults(data) {
            document.getElementById('loading').classList.remove('show');
            
            if (!data.results || data.results.length === 0) {
                document.getElementById('noResults').classList.add('show');
                return;
            }
            
            // Show stats
            document.getElementById('stats').textContent = 
                `Found ${data.results.length} results in ${data.time.toFixed(3)} seconds`;
            
            // Display results
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';
            
            data.results.forEach((result, index) => {
                const resultItem = document.createElement('div');
                resultItem.className = 'result-item';
                
                resultItem.innerHTML = `
                    <h3>${index + 1}. ${escapeHtml(result.title)}</h3>
                    <div class="summary">${escapeHtml(result.summary)}</div>
                    <div class="metadata">
                        <span class="score-badge">Score: ${result.combined_score.toFixed(4)}</span>
                        <span>Text: ${result.text_score.toFixed(3)}</span>
                        <span>PageRank: ${result.pagerank_score.toFixed(3)}</span>
                        <a href="${escapeHtml(result.url)}" target="_blank" class="link">View on Wikipedia →</a>
                    </div>
                `;
                
                resultsDiv.appendChild(resultItem);
            });
            
            resultsDiv.classList.add('show');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
'''


def load_search_engine():
    """
    Load all search engine components
    """
    global ranker, pages_data
    
    try:
        logger.info("Loading search engine components...")
        
        # Load crawled data
        pages_data, _ = WikipediaCrawler.load_data()
        
        # Load PageRank
        pagerank = PageRank.load()
        
        # Load indexer
        indexer = BM25Indexer.load()
        
        # Create ranker
        ranker = SearchRanker(pagerank, indexer)
        
        logger.info("Search engine loaded successfully!")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"Failed to load search engine: {e}")
        logger.error("Please run the pipeline first: crawler.py -> pagerank.py -> indexer.py")
        return False


@app.route('/')
def index():
    """
    Main search page
    """
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/search', methods=['POST'])
def api_search():
    """
    Search API endpoint
    """
    if ranker is None:
        return jsonify({'error': 'Search engine not initialized'}), 500
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    try:
        import time
        start_time = time.time()
        
        # Perform search with detailed scores
        results = ranker.search(query, top_k=20, return_details=True)
        
        search_time = time.time() - start_time
        
        # Format results
        formatted_results = []
        for title, combined, text, pr in results:
            page_data = pages_data.get(title, {})
            
            formatted_results.append({
                'title': title,
                'summary': page_data.get('summary', 'No summary available'),
                'url': page_data.get('url', ''),
                'combined_score': combined,
                'text_score': text,
                'pagerank_score': pr,
            })
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results),
            'time': search_time,
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500


def main():
    """
    Start the web server
    """
    # Load search engine
    if not load_search_engine():
        logger.error("Cannot start web server without search engine data")
        return
    
    # Start Flask app
    logger.info(f"Starting web server at http://{WEB_CONFIG['host']}:{WEB_CONFIG['port']}")
    app.run(
        host=WEB_CONFIG['host'],
        port=WEB_CONFIG['port'],
        debug=WEB_CONFIG['debug']
    )


if __name__ == '__main__':
    main()