"""
Quick Crawler for Fast Testing
Uses direct Wikipedia page titles instead of category exploration

Usage:
    python quick_crawl.py                # Crawl 500 CS pages
    python quick_crawl.py --max-pages 100  # Crawl 100 pages
"""

import wikipediaapi
import json
import logging
import argparse
from typing import Dict, List, Tuple
from Backend.config import CRAWLER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikipediaCrawler:
    """
    Fast crawler using pre-defined list of CS topics
    Much faster than category exploration!
    """
    
    # Curated list of Computer Science topics (500+ topics)
    CS_TOPICS = [
        # Core CS
        "Computer science", "Algorithm", "Data structure", "Programming language",
        "Computer architecture", "Operating system", "Database", "Compiler",
        "Software engineering", "Computer network", "Distributed computing",
        "Theoretical computer science", "Applied computer science", "Computer programming",
        
        # AI/ML (Expanded)
        "Artificial intelligence", "Machine learning", "Deep learning",
        "Neural network", "Natural language processing", "Computer vision",
        "Reinforcement learning", "Supervised learning", "Unsupervised learning",
        "Convolutional neural network", "Recurrent neural network", "Transformer (machine learning)",
        "Gradient descent", "Backpropagation", "Decision tree", "Random forest",
        "Support vector machine", "K-means clustering", "Principal component analysis",
        "Generative adversarial network", "Long short-term memory", "Attention (machine learning)",
        "Transfer learning", "Federated learning", "Meta-learning", "Few-shot learning",
        "Neural architecture search", "AutoML", "Explainable artificial intelligence",
        "Adversarial machine learning", "Model compression", "Knowledge distillation",
        "Ensemble learning", "Boosting (machine learning)", "AdaBoost", "XGBoost",
        "Logistic regression", "Linear regression", "Naive Bayes classifier",
        "K-nearest neighbors algorithm", "Dimensionality reduction", "Feature engineering",
        "Overfitting", "Underfitting", "Regularization (mathematics)", "Cross-validation",
        "Confusion matrix", "Precision and recall", "F-score", "ROC curve",
        
        # More Algorithms
        "Sorting algorithm", "Search algorithm", "Graph algorithm", "Dynamic programming",
        "Greedy algorithm", "Divide and conquer", "Quicksort", "Merge sort",
        "Binary search", "Breadth-first search", "Depth-first search",
        "Dijkstra's algorithm", "A* search algorithm", "Bellman–Ford algorithm",
        "Floyd–Warshall algorithm", "Kruskal's algorithm", "Prim's algorithm",
        "Topological sorting", "Strongly connected component", "Minimum spanning tree",
        "Knapsack problem", "Traveling salesman problem", "Graph coloring",
        "Maximum flow problem", "Shortest path problem", "Hungarian algorithm",
        "Karatsuba algorithm", "Strassen algorithm", "Fast Fourier transform",
        "Insertion sort", "Selection sort", "Bubble sort", "Heap sort",
        "Radix sort", "Counting sort", "Bucket sort", "Shell sort",
        "Interpolation search", "Exponential search", "Jump search", "Fibonacci search",
        
        # Data Structures (Expanded)
        "Array (data structure)", "Linked list", "Stack (abstract data type)",
        "Queue (abstract data type)", "Tree (data structure)", "Binary tree",
        "Binary search tree", "Hash table", "Heap (data structure)", "Graph (abstract data type)",
        "AVL tree", "Red–black tree", "B-tree", "Trie", "Suffix tree",
        "Skip list", "Bloom filter", "Disjoint-set data structure", "Fenwick tree",
        "Segment tree", "Splay tree", "Treap", "Cartesian tree", "K-d tree",
        "Fibonacci heap", "Pairing heap", "Priority queue", "Deque", "Circular buffer",
        
        # Theory (Expanded)
        "Computational complexity theory", "NP-completeness", "Turing machine",
        "Automata theory", "Formal language", "Regular expression", "Context-free grammar",
        "Computability theory", "Lambda calculus", "Church–Turing thesis",
        "Recursion theory", "Decidability", "Halting problem", "Reduction (complexity)",
        "Boolean satisfiability problem", "Polynomial hierarchy", "PSPACE",
        "Quantum complexity theory", "Communication complexity", "Circuit complexity",
        
        # Programming Languages (Expanded)
        "Python (programming language)", "Java (programming language)", "C++", "JavaScript",
        "C (programming language)", "C Sharp (programming language)", "Ruby (programming language)",
        "Go (programming language)", "Rust (programming language)", "Swift (programming language)",
        "Kotlin (programming language)", "TypeScript", "PHP", "Perl", "R (programming language)",
        "MATLAB", "Scala (programming language)", "Haskell", "Erlang (programming language)",
        "Lisp (programming language)", "Scheme (programming language)", "Prolog", "Fortran",
        "COBOL", "Assembly language", "Machine code", "Bytecode",
        
        # Programming Paradigms & Concepts
        "Object-oriented programming", "Functional programming", "Design pattern",
        "Procedural programming", "Declarative programming", "Imperative programming",
        "Logic programming", "Concurrent programming", "Parallel computing",
        "Asynchronous I/O", "Multithreading", "Synchronization (computer science)",
        "Race condition", "Deadlock", "Mutex", "Semaphore (programming)",
        "Monitor (synchronization)", "Lock (computer science)", "Thread pool",
        
        # Software Engineering (Expanded)
        "Version control", "Git", "Software testing", "Debugging",
        "Agile software development", "DevOps", "Continuous integration",
        "Continuous delivery", "Unit testing", "Code review", "Refactoring",
        "Software design pattern", "SOLID", "Don't repeat yourself", "KISS principle",
        "Test-driven development", "Behavior-driven development", "Extreme programming",
        "Scrum (software development)", "Kanban", "Waterfall model", "Spiral model",
        "Software architecture", "Software framework", "Library (computing)",
        "Application programming interface", "Software development kit",
        "Integrated development environment", "Source code", "Documentation",
        
        # Systems (Expanded)
        "Computer hardware", "Central processing unit", "Random-access memory",
        "Hard disk drive", "Solid-state drive", "Cache (computing)",
        "Virtual memory", "Process (computing)", "Thread (computing)",
        "Instruction set architecture", "RISC", "CISC", "Microprocessor",
        "Motherboard", "Graphics card", "Input/output", "Bus (computing)",
        "Direct memory access", "Interrupt", "System call", "Kernel (operating system)",
        "User space and kernel space", "Device driver", "File system",
        "Memory paging", "Memory segmentation", "Context switch", "Scheduling (computing)",
        
        # Operating Systems
        "Linux", "Unix", "Microsoft Windows", "macOS", "Android (operating system)",
        "iOS", "FreeBSD", "OpenBSD", "Solaris (operating system)",
        
        # Networks (Expanded)
        "Internet", "World Wide Web", "HTTP", "TCP/IP", "Router (computing)",
        "Network topology", "Network protocol", "IP address", "Domain Name System",
        "HTTPS", "FTP", "SMTP", "POP3", "IMAP", "SSH (Secure Shell)",
        "Telnet", "Network switch", "Network bridge", "Gateway (telecommunications)",
        "OSI model", "Internet Protocol", "Transmission Control Protocol",
        "User Datagram Protocol", "Internet Protocol version 4", "IPv6",
        "MAC address", "Port (computer networking)", "Socket (networking)",
        "Bandwidth (computing)", "Latency (engineering)", "Packet switching",
        "Circuit switching", "Virtual private network", "Proxy server",
        "Load balancing (computing)", "Content delivery network",
        
        # Security (Expanded)
        "Computer security", "Cryptography", "Encryption", "Public-key cryptography",
        "Digital signature", "Firewall (computing)", "Malware", "Computer virus",
        "Trojan horse (computing)", "Computer worm", "Ransomware", "Spyware",
        "Phishing", "Social engineering (security)", "Denial-of-service attack",
        "Man-in-the-middle attack", "SQL injection", "Cross-site scripting",
        "Authentication", "Authorization", "Access control", "Password",
        "Two-factor authentication", "Biometrics", "Hash function", "Digital certificate",
        "Transport Layer Security", "Secure Sockets Layer", "Pretty Good Privacy",
        "Advanced Encryption Standard", "RSA (cryptosystem)", "Diffie–Hellman key exchange",
        
        # Databases (Expanded)
        "Relational database", "SQL", "NoSQL", "Database normalization",
        "ACID", "Database transaction", "Query language", "Data mining",
        "Database index", "Primary key", "Foreign key", "Join (SQL)",
        "MySQL", "PostgreSQL", "Oracle Database", "Microsoft SQL Server",
        "MongoDB", "Redis", "Cassandra (database)", "Neo4j",
        "Database management system", "Entity–relationship model", "Data warehouse",
        "Online analytical processing", "Extract, transform, load",
        "Database schema", "Stored procedure", "Trigger (database)",
        
        # Web Technologies (Expanded)
        "Web development", "HTML", "CSS", "Web browser", "Client–server model",
        "REST", "API", "Web application", "Web service",
        "JavaScript framework", "React (software)", "Angular (web framework)",
        "Vue.js", "Node.js", "Express.js", "Django (web framework)",
        "Ruby on Rails", "Spring Framework", "ASP.NET",
        "Responsive web design", "Progressive web application", "Single-page application",
        "WebSocket", "Ajax (programming)", "JSON", "XML",
        "Web scraping", "Search engine optimization", "Web hosting service",
        
        # Software Development Tools
        "Continuous integration", "Unit testing", "Code review",
        "Jenkins (software)", "Travis CI", "CircleCI", "GitHub",
        "GitLab", "Bitbucket", "Docker (software)", "Kubernetes",
        "Ansible (software)", "Terraform (software)", "Maven", "Gradle",
        
        # Computer Graphics (Expanded)
        "Computer graphics", "3D computer graphics", "Rendering (computer graphics)",
        "Ray tracing (graphics)", "Graphics processing unit", "OpenGL",
        "DirectX", "Vulkan (API)", "Shader", "Texture mapping",
        "Rasterisation", "3D modeling", "Computer animation", "Virtual reality",
        "Augmented reality", "Image processing", "Digital image processing",
        
        # Emerging Technologies
        "Quantum computing", "Blockchain", "Cloud computing", "Internet of things",
        "Big data", "Data science", "Bioinformatics", "Computational biology",
        "Robotics", "Autonomous vehicle", "Edge computing", "Fog computing",
        "5G", "Augmented reality", "Mixed reality", "Brain–computer interface",
        "Quantum cryptography", "Neuromorphic engineering",
        
        # AI Applications
        "Expert system", "Fuzzy logic", "Genetic algorithm", "Evolutionary computation",
        "Swarm intelligence", "Ant colony optimization", "Particle swarm optimization",
        "Simulated annealing", "Artificial life", "Cellular automaton",
        "Game theory", "Multi-agent system", "Intelligent agent",
        
        # Programming Concepts (Expanded)
        "Recursion", "Iteration", "Variable (computer science)", "Function (programming)",
        "Pointer (computer programming)", "Memory management", "Garbage collection (computer science)",
        "Reference (computer science)", "Value (computer science)", "Expression (computer science)",
        "Statement (computer science)", "Control flow", "Exception handling",
        "Scope (computer science)", "Closure (computer programming)", "Lambda expression",
        "Higher-order function", "Currying", "Lazy evaluation", "Memoization",
        
        # Software Architecture (Expanded)
        "Microservices", "Service-oriented architecture", "Model–view–controller",
        "Client–server model", "Peer-to-peer", "Message passing",
        "Event-driven architecture", "Layered architecture", "Hexagonal architecture",
        "CQRS", "Event sourcing", "Domain-driven design",
        
        # Complexity & Analysis
        "Time complexity", "Space complexity", "Big O notation", "NP-hard",
        "P versus NP problem", "Computational complexity",
        "Big Theta notation", "Big Omega notation", "Amortized analysis",
        "Asymptotic analysis", "Master theorem",
        
        # Compilers & Languages
        "Compiler", "Interpreter (computing)", "Lexical analysis", "Parsing",
        "Abstract syntax tree", "Intermediate representation", "Code generation",
        "Optimization (computer science)", "Just-in-time compilation",
        
        # Distributed Systems
        "Distributed computing", "Distributed database", "Distributed algorithm",
        "Consensus (computer science)", "Byzantine fault", "CAP theorem",
        "MapReduce", "Apache Hadoop", "Apache Spark",
        
        # More CS Topics
        "Information theory", "Coding theory", "Error detection and correction",
        "Data compression", "Lossless compression", "Lossy compression",
        "Huffman coding", "Arithmetic coding", "Run-length encoding",
        "Computer simulation", "Monte Carlo method", "Numerical analysis",
        "Computational geometry", "Computational linguistics", "Digital signal processing",
        "Pattern recognition", "Computer-aided design", "Geographic information system",
    ]
    
    def __init__(self, max_pages: int = None):
        """Initialize quick crawler"""
        self.max_pages = max_pages or min(500, len(self.CS_TOPICS))
        
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='PageRankSearchEngine/1.0 (Education Project)',
            language='en'
        )
        
        self.pages_data = {}
        self.link_graph = {}
        self.visited = set()
    
    def crawl(self) -> Tuple[Dict, Dict]:
        """
        Crawl predefined CS topics quickly
        """
        logger.info(f"Quick crawling {self.max_pages} Computer Science pages...")
        
        import time
        start_time = time.time()
        
        # Crawl from our curated list
        topics_to_crawl = self.CS_TOPICS[:self.max_pages]
        
        for i, topic in enumerate(topics_to_crawl, 1):
            if len(self.visited) >= self.max_pages:
                break
            
            self._crawl_page(topic)
            
            # Progress
            if i % 20 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                remaining = self.max_pages - i
                eta = remaining / rate if rate > 0 else 0
                logger.info(f"Progress: {i}/{self.max_pages} pages "
                          f"({rate:.1f} pages/sec, ETA: {eta/60:.1f} min)")
        
        logger.info(f"Quick crawl complete! Crawled {len(self.visited)} pages in {(time.time()-start_time)/60:.1f} minutes")
        return self.pages_data, self.link_graph
    
    def _crawl_page(self, page_title: str):
        """Crawl a single page"""
        if page_title in self.visited:
            return
        
        page = self.wiki.page(page_title)
        
        if not page.exists():
            return
        
        self.visited.add(page_title)
        
        # Extract page content
        self.pages_data[page_title] = {
            'title': page.title,
            'text': page.text[:5000],
            'summary': page.summary,
            'url': page.fullurl,
            'categories': [cat for cat in page.categories.keys()],
        }
        
        # Extract links (limit to first 50 to save time)
        links = []
        for link_title in list(page.links.keys())[:50]:
            if not any(prefix in link_title for prefix in ['File:', 'Category:', 'Wikipedia:', 'Help:', 'Template:']):
                if self.wiki.page(link_title).exists():
                    links.append(link_title)
        
        self.link_graph[page_title] = links
    
    def save_data(self, pages_file: str = None, graph_file: str = None):
        """Save data"""
        pages_file = pages_file or CRAWLER_CONFIG['output_file']
        graph_file = graph_file or CRAWLER_CONFIG['graph_file']
        
        with open(pages_file, 'w', encoding='utf-8') as f:
            json.dump(self.pages_data, f, indent=2, ensure_ascii=False)
        
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(self.link_graph, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Saved {len(self.pages_data)} pages to {pages_file}")

    @staticmethod
    def load_data(pages_file: str = None, graph_file: str = None):
        """
        Load previously crawled data
        
        Args:
            pages_file: Path to pages data JSON
            graph_file: Path to link graph JSON
            
        Returns:
            Tuple of (pages_data, link_graph)
        """
        from Backend.config import CRAWLER_CONFIG
        
        pages_file = pages_file or CRAWLER_CONFIG['output_file']
        graph_file = graph_file or CRAWLER_CONFIG['graph_file']
        
        with open(pages_file, 'r', encoding='utf-8') as f:
            pages_data = json.load(f)
        
        with open(graph_file, 'r', encoding='utf-8') as f:
            link_graph = json.load(f)
        
        logger.info(f"Loaded {len(pages_data)} pages and link graph")
        return pages_data, link_graph

def main():
    parser = argparse.ArgumentParser(description='Quick Wikipedia Crawler')
    parser.add_argument('--max-pages', type=int, default=500,
                       help='Maximum pages to crawl (default: 500)')
    args = parser.parse_args()
    
    crawler = WikipediaCrawler(max_pages=args.max_pages)
    pages_data, link_graph = crawler.crawl()
    crawler.save_data()
    
    print(f"\n{'='*80}")
    print(f"✓ Quick crawl complete!")
    print(f"  Pages crawled: {len(pages_data)}")
    print(f"  Total links: {sum(len(links) for links in link_graph.values())}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()