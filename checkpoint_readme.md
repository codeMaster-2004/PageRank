# PageRank Search Engine - Checkpoint Presentation Guide

## 🎯 Project Overview

**Project Name**: PageRank Search Engine for Computer Science Topics

**Goal**: Build a complete search engine that combines Google's PageRank algorithm with BM25 text retrieval to intelligently rank Wikipedia Computer Science pages.

**Key Innovation**: We merge structural importance (PageRank) with content relevance (BM25) using a weighted combination (70% text + 30% PageRank).

---

## 👥 Team Members & Responsibilities

| Name | Email | Component | What You Built |
|------|-------|-----------|----------------|
| **Gulnaaz Sayyad** | gsayy2@illinois.edu | Crawler | Wikipedia data collection & link graph |
| **Kundan Mergu** | kmerg2@illinois.edu | PageRank + Evaluator | PageRank algorithm + Evaluation metrics |
| **Teja Nerella** | nerella2@illinois.edu | Indexer | BM25 inverted index & text processing |
| **Abhiram Annaluru** | abhia2@illinois.edu | Ranker | Combined ranking engine |

**Note**: Kundan took over PageRank implementation from Shikhar.

---

## 📊 Project Results Summary

### What We Accomplished:
- ✅ Crawled **249 Wikipedia CS pages**
- ✅ Built link graph with **4,746 unique pages** referenced
- ✅ PageRank converged in **19 iterations** (~1 minute)
- ✅ Indexed **10,910 unique terms**
- ✅ Query response time: **~10-50ms**
- ✅ Full pipeline runtime: **24.35 minutes**
- ✅ Working web interface with real-time search

### Key Metrics:
```
Graph Size: 249 crawled pages → 4,746 nodes in graph
Average Links: ~19 outgoing links per page
PageRank Convergence: 19 iterations (threshold: 1e-6)
Search Index: 10,910 terms
Average Document Length: 592 words
```

---

## 🎤 Individual Talking Points

### 1️⃣ Gulnaaz Sayyad - Crawler & Data Acquisition

#### **What You Built:**
- Wikipedia crawler using `wikipediaapi` library
- Collected 249 Computer Science pages with curated topic list
- Built directed link graph for PageRank computation

#### **Your Talking Points:**

**1. Crawler Design (2-3 minutes)**
> "I implemented a focused crawler that collects Wikipedia Computer Science pages. Instead of random crawling, we use a curated list of 400+ CS topics including AI/ML, algorithms, data structures, systems, and security topics."

**2. Implementation Details:**
```python
# Key features:
- Direct page download (no BFS link following)
- Extracts: title, text, summary, categories, URLs
- Builds link graph: page → list of outgoing links
- Rate: ~10-15 pages per minute (Wikipedia API limits)
```

**3. Results:**
> "We successfully crawled 249 pages in ~19 minutes. Each page links to an average of 19 other pages, creating a rich graph structure with 4,746 unique nodes. This dense connectivity was crucial for effective PageRank computation."

**4. Technical Challenges:**
- Wikipedia API rate limiting (1 second per request)
- Filtering out non-article pages (Files, Categories, Templates)
- Handling missing or redirect pages
- Memory-efficient link extraction (limited to 50 links per page)

**5. Data Format:**
```json
{
  "Machine learning": {
    "title": "Machine learning",
    "text": "ML is a field of AI...",
    "summary": "Short description...",
    "url": "https://en.wikipedia.org/wiki/Machine_learning",
    "categories": ["Artificial intelligence", ...]
  }
}
```

**Demo What to Show:**
- Show `Backend/data/crawled_pages.json` (sample pages)
- Show link graph structure in `Backend/data/page_graph.json`
- Run: `python -m Backend.web_crawler --max-pages 10` (quick demo)

---

### 2️⃣ Kundan Mergu - PageRank Algorithm & Evaluation

#### **What You Built:**
- PageRank algorithm using power iteration
- Evaluation framework with Precision, Recall, NDCG
- Performance benchmarking system

#### **Your Talking Points:**

**1. PageRank Algorithm (3-4 minutes)**

> "I implemented Google's PageRank algorithm, which determines page importance based on the link structure. The key insight: a page is important if many important pages link to it."

**PageRank Formula:**
```
PR(p) = (1-d)/N + d × Σ(PR(q) / L(q))

Where:
- d = 0.85 (damping factor - probability of following a link)
- N = total pages
- PR(q) = PageRank of pages linking to p
- L(q) = number of outgoing links from q
```

**2. Implementation Details:**
```python
# Power iteration method:
1. Initialize all pages with equal rank (1/N)
2. Iteratively update ranks using formula
3. Stop when change < 1e-6 (L1 norm)
4. Converged in 19 iterations for our graph
```

**3. Key Results:**
```
Top 5 Pages by PageRank:
1. ArXiv (identifier)       - 0.002776  ← Most referenced
2. Algorithm                 - 0.002239  ← Core CS concept
3. Doi (identifier)          - 0.001974  ← Citation system
4. Associative array         - 0.001946  ← Fundamental structure
5. Bibcode (identifier)      - 0.001918  ← Reference system
```

**4. Interesting Insight:**
> "Citation identifiers (ArXiv, Doi, Bibcode) ranked highest. This makes sense - they appear in the 'References' section of almost every CS paper on Wikipedia. This validates our algorithm: PageRank correctly identifies the most-linked pages!"

**5. Evaluation Framework:**

You also built evaluation metrics:

**Metrics Implemented:**
- **Precision@k**: Fraction of retrieved results that are relevant
- **Recall@k**: Fraction of relevant documents retrieved  
- **F1 Score**: Harmonic mean of precision & recall
- **NDCG@k**: Normalized Discounted Cumulative Gain (considers ranking order)

**Performance Results:**
- Query response time: 10-50ms
- PageRank computation: ~1 minute for 4,746 nodes
- Convergence: 19 iterations vs theoretical 30-50

**Demo What to Show:**
- Show PageRank convergence logs
- Show top 10 ranked pages
- Run: `python -m Backend.pagerank` (recompute demo)
- Show evaluation comparison (with vs without PageRank)

---

### 3️⃣ Teja Nerella - Indexing & Text Processing

#### **What You Built:**
- BM25 inverted index for fast text search
- Text preprocessing pipeline
- Query-time scoring system

#### **Your Talking Points:**

**1. BM25 Algorithm (2-3 minutes)**

> "I implemented BM25, a state-of-the-art text retrieval algorithm used by search engines. It improves on TF-IDF by considering document length and term saturation."

**BM25 Formula:**
```
BM25(D,Q) = Σ IDF(qi) × (f(qi,D) × (k1+1)) / (f(qi,D) + k1 × (1-b + b×|D|/avgdl))

Where:
- IDF = Inverse Document Frequency (how rare is the term)
- f(qi,D) = term frequency in document
- k1 = 1.5 (term frequency saturation)
- b = 0.75 (length normalization)
- |D| = document length
- avgdl = average document length
```

**2. Text Processing Pipeline:**
```python
1. Lowercase conversion
2. Remove URLs and punctuation
3. Tokenization (split into words)
4. Stop word removal ("the", "is", "and", etc.)
5. Minimum length filter (≥3 characters)
```

**3. Inverted Index Structure:**
```python
{
  "machine": [(doc_1, freq=5), (doc_3, freq=2), ...],
  "learning": [(doc_1, freq=3), (doc_2, freq=7), ...],
  "algorithm": [(doc_5, freq=4), (doc_8, freq=1), ...]
}
```

**4. Key Results:**
```
Index Statistics:
- Total terms indexed: 10,910 unique terms
- Average document length: 592 words
- Indexing time: ~30 seconds for 249 documents
- Index size: ~2-3 MB (in memory)
```

**5. Title Boosting:**
> "We boost title words by 3x to prioritize documents where query terms appear in the title. This significantly improves search quality."

**6. Search Example:**
```
Query: "machine learning"

Results:
1. "Machine learning" - BM25: 0.9941 (title match!)
2. "AutoML" - BM25: 1.0000 (perfect match)
3. "Transfer learning" - BM25: 0.8092 (contains both terms)
```

**Demo What to Show:**
- Show inverted index structure
- Show text preprocessing example
- Run: `python -m Backend.indexer` (build index demo)
- Search for a query and show BM25 scores

---

### 4️⃣ Abhiram Annaluru - Ranking & Query Engine

#### **What You Built:**
- Combined ranking engine (BM25 + PageRank)
- Score normalization and weighting system
- Query processing and result ranking

#### **Your Talking Points:**

**1. Combined Ranking Strategy (2-3 minutes)**

> "My component merges text relevance with structural importance. The key challenge: how do we combine BM25 scores (0-100+) with PageRank scores (0.001-0.003)? Answer: normalize both to 0-1 range, then use weighted sum."

**Ranking Formula:**
```
FinalScore = 0.7 × NormalizedBM25 + 0.3 × NormalizedPageRank

Normalization:
- BM25: (score - min) / (max - min)
- PageRank: (score - min) / (max - min)
```

**2. Why 70-30 Split?**
> "We chose 70% text and 30% PageRank because text relevance should dominate - users want pages about their query! But PageRank helps break ties and boost authoritative pages."

**3. Example: "machine learning" Query:**

| Rank | Page | Combined | Text | PageRank | Why This Ranking? |
|------|------|----------|------|----------|-------------------|
| 1 | Machine learning | 0.7037 | 0.9941 | 0.0260 | High text match |
| 2 | AutoML | 0.7000 | 1.0000 | 0.0000 | Perfect text match |
| 3 | Adversarial ML | 0.6736 | 0.9029 | 0.1385 | **PageRank boost!** |
| 4 | Transfer learning | 0.5664 | 0.8092 | 0.0000 | Good text match |
| 5 | Deep learning | 0.5264 | 0.7258 | 0.0612 | Related topic |

**4. Key Insight:**
> "Notice rank #3: 'Adversarial ML' has slightly lower text score than 'Transfer learning', but it ranks higher because of its PageRank score (0.1385). This shows our combined ranking successfully identifies pages that are both relevant AND authoritative!"

**5. Query Processing Flow:**
```
User Query
    ↓
Text Preprocessing (lowercase, tokenize)
    ↓
BM25 Search → Get top 100 candidates
    ↓
Normalize Scores (0-1 range)
    ↓
Apply PageRank Scores
    ↓
Weighted Combination (70-30)
    ↓
Sort by Final Score
    ↓
Return Top K Results
```

**6. Performance:**
- Query time: 10-50ms for most queries
- Handles concurrent searches (Flask web server)
- Scalable to 1000+ documents easily

**Demo What to Show:**
- Show side-by-side comparison (BM25 only vs Combined)
- Search for same query twice to show consistency
- Run: `python -m Backend.ranker` (show comparison)
- Demonstrate web interface live searches

---

## 🖥️ Live Demo Script (5-7 minutes)

### Demo Flow:

**1. Start Web Interface (1 min)**
```bash
# Show terminal
python -m Backend.main --serve

# Open browser to http://localhost:5001
```

**2. Search Examples (3-4 min)**

**Query 1: "machine learning"**
> "Let's search for 'machine learning'. Notice the top result is the main ML article with high combined score. AutoML ranks #2 despite perfect text match because it has lower PageRank."

**Query 2: "graph algorithms"**
> "Searching for 'graph algorithms' shows how our system finds relevant pages about graphs, algorithms, and related data structures."

**Query 3: "neural networks"**
> "This query demonstrates how we handle multi-word queries and rank pages about deep learning, CNNs, and AI."

**3. Show Score Breakdown (2 min)**
> "For each result, you can see three scores:
> - **Combined Score**: Final ranking (70% text + 30% PageRank)
> - **Text Score**: How well the content matches the query
> - **PageRank Score**: How important the page is by link structure
> 
> This transparency helps us validate that our algorithm is working correctly."

**4. Click Through to Wikipedia (1 min)**
> "Each result links to the actual Wikipedia page, so users can read the full article."

---

## 📈 System Architecture Diagram

```
                    USER QUERY
                        ↓
              ┌─────────────────────┐
              │   Web Interface     │
              │   (Flask + HTML)    │
              └─────────┬───────────┘
                        ↓
              ┌─────────────────────┐
              │  Ranking Engine     │  ← Abhiram
              │  (Combined Scores)  │
              └───────┬─────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌───────────────┐           ┌──────────────┐
│  BM25 Indexer │           │  PageRank    │
│  (Text Score) │  ← Teja   │  (Authority) │  ← Kundan
└───────┬───────┘           └──────┬───────┘
        ↓                          ↓
┌───────────────────────────────────────┐
│         Crawled Wikipedia Data        │  ← Gulnaaz
│      (Pages + Link Graph)             │
└───────────────────────────────────────┘
```

---

## 🎓 Technical Highlights for Q&A

### **PageRank Convergence:**
- **Q**: Why did you use 0.85 damping factor?
- **A**: "0.85 is the standard value used by Google. It means 85% probability of following a link, 15% random jump. This prevents getting stuck in loops and ensures convergence."

### **BM25 vs TF-IDF:**
- **Q**: Why BM25 instead of TF-IDF?
- **A**: "BM25 is superior because: (1) it has term frequency saturation - after certain point, more occurrences don't help much, and (2) it normalizes for document length, so longer docs aren't unfairly penalized."

### **Evaluation Metrics:**
- **Q**: How do you know your system works well?
- **A**: "We use standard IR metrics: Precision (how many results are relevant), Recall (how many relevant docs we found), and NDCG (considers ranking order and relevance grades). We also compare with/without PageRank to show it adds value."

### **Scalability:**
- **Q**: Can this scale to millions of pages?
- **A**: "Our current implementation works well for thousands of pages. For millions, we'd need: (1) distributed PageRank computation (e.g., MapReduce), (2) inverted index sharding, (3) caching layer, and (4) specialized search infrastructure like Elasticsearch."

### **Why Citation Pages Rank Highest:**
- **Q**: Why do ArXiv and Doi rank higher than 'Algorithm'?
- **A**: "This is actually correct! Citation identifiers appear in the References section of nearly every Wikipedia CS article. PageRank measures link structure, not semantic importance. This highlights an interesting property: metadata pages are structurally more 'important' than content pages in academic contexts."

---

## 📊 Checkpoint Presentation Structure (15-20 minutes)

### **Slide 1: Title & Team** (1 min)
- Project name
- Team members with photos/roles
- Course info

### **Slide 2: Problem Statement** (2 min)
- Challenge: Finding relevant AND authoritative CS information
- Solution: Combine text matching (BM25) with link analysis (PageRank)

### **Slide 3: System Architecture** (2 min)
- Show architecture diagram
- Explain data flow

### **Slide 4-7: Individual Components** (8 min, 2 min each)
- Gulnaaz: Crawler
- Kundan: PageRank + Evaluation
- Teja: BM25 Indexer
- Abhiram: Combined Ranker

### **Slide 8: Results & Metrics** (2 min)
- Show key statistics
- Performance numbers
- Top PageRank pages

### **Slide 9: Live Demo** (5 min)
- Show web interface
- Run 3-4 sample queries
- Explain scores

### **Slide 10: Conclusions & Next Steps** (2 min)
- What we learned
- Potential improvements
- Q&A

---

## 🚀 Quick Commands Reference

```bash
# Run full pipeline (if data missing)
python -m Backend.main --full-pipeline --max-pages 250

# Individual components
python -m Backend.main --crawl --max-pages 250
python -m Backend.main --pagerank
python -m Backend.main --index

# Search from terminal
python -m Backend.main --search "machine learning"

# Start web interface
python -m Backend.main --serve

# Open browser to:
http://localhost:5001
```

---

## 📁 Important Files to Know

```
Backend/
├── web_crawler.py      - Gulnaaz's crawler
├── pagerank.py         - Kundan's PageRank
├── indexer.py          - Teja's BM25 indexer
├── ranker.py           - Abhiram's ranking engine
├── evaluator.py        - Kundan's evaluation
├── config.py           - All settings (change port here!)
├── data/
│   ├── crawled_pages.json   - Your 249 pages
│   └── page_graph.json      - Link structure
├── index/
│   └── inverted_index.pkl   - BM25 index
└── results/
    └── pagerank_scores.pkl  - PageRank results

Frontend/
└── app.py              - Flask web interface
```

---

## ✅ Pre-Checkpoint Checklist

**Everyone:**
- [ ] Read this entire README
- [ ] Understand your component
- [ ] Know your talking points
- [ ] Test running your component individually
- [ ] Practice explaining your algorithm

**Gulnaaz:**
- [ ] Can explain crawler design
- [ ] Show crawled data files
- [ ] Know: 249 pages, ~19 links/page

**Kundan:**
- [ ] Can explain PageRank formula
- [ ] Show convergence (19 iterations)
- [ ] Know top 5 ranked pages
- [ ] Explain evaluation metrics

**Teja:**
- [ ] Can explain BM25 formula
- [ ] Show inverted index
- [ ] Know: 10,910 terms indexed
- [ ] Explain text preprocessing

**Abhiram:**
- [ ] Can explain 70-30 weighting
- [ ] Show score normalization
- [ ] Demo web interface
- [ ] Compare BM25 vs Combined

**Demo Setup:**
- [ ] Web interface works (port 5001)
- [ ] Can search multiple queries
- [ ] All data files present
- [ ] No errors in terminal

---

## 🎯 Key Takeaways for Checkpoint

**What went well:**
- ✅ Complete end-to-end system working
- ✅ All algorithms implemented correctly
- ✅ PageRank converged quickly (19 iterations)
- ✅ Web interface is polished and functional
- ✅ Good performance (10-50ms queries)

**Interesting findings:**
- Citation identifiers rank highest by PageRank (validates algorithm!)
- Combined ranking successfully balances relevance and authority
- BM25 with title boosting works very well

**What we'd improve:**
- Scale to more pages (currently 249)
- Add query suggestions/autocomplete
- Implement personalized PageRank
- Add more evaluation with user studies
- Optimize for production deployment

---

## 💡 Final Tips for Presentation

1. **Be confident** - Your system works well!
2. **Use concrete examples** - Show actual queries and results
3. **Explain trade-offs** - Why you chose certain parameters
4. **Show enthusiasm** - This is cool stuff!
5. **Prepare for questions** - Read the Q&A section
6. **Time yourselves** - Practice to hit 15-20 minutes
7. **Have backup slides** - In case demo fails

**Good luck with your checkpoint! 🚀**

---

**Questions?** Contact:
- Kundan (PageRank/Eval): kmerg2@illinois.edu
- Gulnaaz (Crawler): gsayy2@illinois.edu
- Teja (Indexer): nerella2@illinois.edu
- Abhiram (Ranker): abhia2@illinois.edu
