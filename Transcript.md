🎥 3-Minute Group Demo Script (4 Speakers, 180 Seconds)

🧑‍💻 Speaker 1 — Gulnaaz (Crawler & Data) — ~45 seconds

“Hi everyone, I’m Gulnaaz, and I built the data acquisition pipeline behind our search engine.
We wanted high-quality Computer Science content, so instead of crawling the whole web, I built a focused Wikipedia crawler that collects pages only from CS-related topics—AI, algorithms, data structures, systems, and more.

Using the Wikipedia API, we gathered 249 pages and extracted each page’s title, text, summary, categories, and outgoing links.
Those links let us build a directed graph with 4,700+ nodes, which later powers our PageRank algorithm.

This dataset gives us both the text needed for BM25 search and the network structure needed to model page importance.”

🧑‍🔬 Speaker 2 — Kundan (PageRank) — ~45 seconds

“I’m Kundan, and I implemented the PageRank algorithm—the same algorithm originally used by Google.

The idea is simple:
A page is important if many important pages link to it.

We compute PageRank using power iteration, and on our CS graph it converges in 19 iterations.
This gives every page a numeric authority score—usually between 0.001 and 0.003.

As an example, ‘Adversarial Machine Learning’ has a PageRank score of 0.139 (normalized), which is surprisingly high because many ML-related pages reference it.
You’ll see how that influences its ranking when we search later.”

🧑‍🏫 Speaker 3 — Teja (BM25 Indexing) — ~40 seconds

“I’m Teja, and I implemented the BM25 search engine that handles text relevance.

I built a tokenizer that cleans the text, removes stopwords, and constructs an inverted index with over 10,000 unique terms.
Each query is scored using BM25, which accounts for term frequency, document length, and keyword rarity.

For example, when you search ‘machine learning,’ the ‘Machine Learning’ page gets a Text Score of 0.971, which is extremely high because the term appears frequently in both the title and the body.

BM25 alone gives us strong textual relevance—but combining it with PageRank gives us much better rankings.”

🧑‍💻 Speaker 4 — Abhiram (Ranking Engine + Final Demo) — ~45 seconds

“I’m Abhiram, and I built the final ranking engine and web interface.

My component takes Teja’s BM25 scores and Kundan’s PageRank scores, normalizes everything to a 0–1 scale, and combines them using a 70% text weight and 30% PageRank weight.

Let’s look at the example shown here.
When we search for ‘machine learning’, the top result is ‘Adversarial Machine Learning’ with:

Combined Score: 0.7214

Text Score: 0.971

PageRank: 0.139

This page is ranked highly not just because it matches the topic, but also because its PageRank score shows it’s authoritative in the ML ecosystem.
The interface displays all three scores so you can see exactly why it ranks where it does.

That completes our 3-minute demo—thank you!”