# PageRank Search Engine

A Wikipedia search engine that ranks results with **BM25 text relevance** and **PageRank link authority**. It crawls a curated set of computer-science pages, builds a link graph, computes PageRank via power iteration, indexes titles/summaries with BM25, and serves results through a Flask UI.

## How ranking works

Each query is scored as:

```
combined = 0.7 × normalized BM25 + 0.3 × normalized PageRank
```

Weights live in `Backend/config.py` (`RANKER_CONFIG`). PageRank uses damping `0.85` and L1 convergence `1e-6`.

```
Wikipedia CS pages
        │
        ▼
   Crawler ──► pages JSON + link graph
        │
        ├──────────────► PageRank scores
        └──────────────► BM25 inverted index
                         │
                         ▼
                    SearchRanker
                         │
                         ▼
              CLI search / Flask UI
```

## Requirements

- Python 3.7+
- Dependencies in `requirements.txt` (`wikipedia-api`, `numpy`, `Flask`)

```bash
git clone https://github.com/codeMaster-2004/PageRank.git
cd PageRank
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run commands from the **repo root** so `Backend` / `Frontend` imports resolve.

## Quick start

Crawl ~250 CS Wikipedia pages, compute PageRank, build the index, then search:

```bash
python3 -m Backend.main --full-pipeline --max-pages 250
python3 -m Backend.main --search "machine learning"
python3 -m Backend.main --serve
```

The UI starts at [http://localhost:5001](http://localhost:5001) (`WEB_CONFIG` in `Backend/config.py`).

## CLI

```bash
python3 -m Backend.main --help
python3 -m Backend.main --crawl --max-pages 250
python3 -m Backend.main --index
python3 -m Backend.main --search "neural networks"
python3 -m Backend.main --evaluate
python3 -m Backend.main --serve
```

With no flags, `Backend.main` opens an interactive menu (full pipeline / search / web server).

`Backend/run_pipeline.py` is an older sequential runner that imports modules as if they lived next to the script (`from crawler import ...`). Prefer `python3 -m Backend.main`.

## Project layout

```
PageRank/
├── Backend/
│   ├── main.py            # Orchestrator: crawl → PageRank → index → search/serve
│   ├── web_crawler.py     # Wikipedia crawler (curated CS topic list)
│   ├── pagerank.py        # Power-iteration PageRank
│   ├── indexer.py         # BM25 inverted index
│   ├── ranker.py          # Combined BM25 + PageRank scoring
│   ├── evaluator.py       # NDCG-style eval vs BM25-only
│   ├── config.py          # Damping, BM25 params, weights, ports
│   ├── data/              # crawled_pages.json, page_graph.json
│   ├── index/             # inverted_index.pkl
│   └── results/           # pagerank_scores.json / .pkl
├── Frontend/
│   └── app.py             # Flask search UI + /api/search
└── requirements.txt
```

## Configuration

Edit `Backend/config.py`:

| Setting | Default | Meaning |
|---|---|---|
| `CRAWLER_CONFIG['max_pages']` | 500 | Crawl cap |
| `PAGERANK_CONFIG['damping_factor']` | 0.85 | Probability of following a link |
| `INDEXER_CONFIG['bm25_k1']` / `bm25_b` | 1.5 / 0.75 | BM25 parameters |
| `RANKER_CONFIG['text_weight']` | 0.7 | BM25 share of the combined score |
| `RANKER_CONFIG['pagerank_weight']` | 0.3 | PageRank share |
| `WEB_CONFIG['port']` | 5001 | Flask port |

## Notes

- The crawler uses a hand-picked CS topic list (algorithms, ML, languages, systems) rather than walking Wikipedia categories.
- Pipeline artifacts are already checked in under `Backend/data`, `Backend/index`, and `Backend/results`, so `--search` / `--serve` can work without recrawling.
- `__pycache__` is currently in the repo; it is safe to ignore locally.

