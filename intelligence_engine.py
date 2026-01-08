"""
Intelligence Engine Module - AI-POWERED BREAKTHROUGHS
Advanced semantic analysis, knowledge graphs, and intelligent features
"""

import re
import json
import math
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import hashlib

try:
    import sqlite3
except ImportError:
    sqlite3 = None


class SemanticSearchEngine:
    """Advanced semantic search with TF-IDF and cosine similarity"""

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Set[str] = set()
        self.idf_scores: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []

    def add_document(self, doc_id: str, title: str, content: str):
        """Add a document to the semantic index"""
        doc = {
            "id": doc_id,
            "title": title,
            "content": content,
            "tokens": self._tokenize(f"{title} {content}")
        }
        self.documents.append(doc)
        self.vocabulary.update(doc["tokens"])

    def _tokenize(self, text: str) -> List[str]:
        """Advanced tokenization with stemming-like normalization"""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())

        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
            'have', 'has', 'had', 'will', 'would', 'could', 'should', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'i',
            'you', 'we', 'they', 'them', 'their', 'what', 'which', 'who', 'when',
            'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'just', 'now'
        }

        # Filter and normalize
        tokens = [w for w in words if len(w) > 2 and w not in stop_words]
        return tokens

    def build_index(self):
        """Build TF-IDF index for all documents"""
        if not self.documents:
            return

        # Calculate IDF scores
        doc_count = len(self.documents)
        word_doc_count = defaultdict(int)

        for doc in self.documents:
            unique_words = set(doc["tokens"])
            for word in unique_words:
                word_doc_count[word] += 1

        for word, count in word_doc_count.items():
            self.idf_scores[word] = math.log(doc_count / count)

        # Build TF-IDF vectors for each document
        self.doc_vectors = []
        for doc in self.documents:
            vector = self._compute_tfidf_vector(doc["tokens"])
            self.doc_vectors.append(vector)

    def _compute_tfidf_vector(self, tokens: List[str]) -> Dict[str, float]:
        """Compute TF-IDF vector for a list of tokens"""
        # Calculate term frequency
        tf = Counter(tokens)
        total_terms = len(tokens)

        vector = {}
        for term, count in tf.items():
            tf_score = count / total_terms if total_terms > 0 else 0
            idf_score = self.idf_scores.get(term, 0)
            vector[term] = tf_score * idf_score

        return vector

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Semantic search using cosine similarity"""
        if not self.documents:
            return []

        query_tokens = self._tokenize(query)
        query_vector = self._compute_tfidf_vector(query_tokens)

        # Calculate cosine similarity with each document
        similarities = []
        for i, doc_vector in enumerate(self.doc_vectors):
            similarity = self._cosine_similarity(query_vector, doc_vector)
            similarities.append({
                "doc_index": i,
                "similarity": similarity,
                "doc": self.documents[i]
            })

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Get intersection of terms
        common_terms = set(vec1.keys()) & set(vec2.keys())

        if not common_terms:
            return 0.0

        # Calculate dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)

        # Calculate magnitudes
        mag1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val ** 2 for val in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def get_similar_documents(self, doc_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find documents similar to a given document"""
        # Find the document
        doc_index = None
        for i, doc in enumerate(self.documents):
            if doc["id"] == doc_id:
                doc_index = i
                break

        if doc_index is None:
            return []

        doc_vector = self.doc_vectors[doc_index]

        # Calculate similarities
        similarities = []
        for i, other_vector in enumerate(self.doc_vectors):
            if i == doc_index:
                continue
            similarity = self._cosine_similarity(doc_vector, other_vector)
            similarities.append({
                "doc_index": i,
                "similarity": similarity,
                "doc": self.documents[i]
            })

        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]


class SourceCredibilityScorer:
    """Intelligent source credibility and authority scoring"""

    def __init__(self):
        # Domain authority scores (simplified - in production, use real API)
        self.trusted_domains = {
            # Academic and Research
            'edu': 0.95, 'arxiv.org': 0.95, 'nature.com': 0.95, 'science.org': 0.95,
            'ieee.org': 0.95, 'acm.org': 0.95, 'pubmed.ncbi.nlm.nih.gov': 0.95,

            # Government and Official
            'gov': 0.90, 'who.int': 0.90, 'un.org': 0.90, 'europa.eu': 0.90,

            # Major News Organizations
            'reuters.com': 0.85, 'apnews.com': 0.85, 'bbc.com': 0.85, 'npr.org': 0.85,
            'theguardian.com': 0.80, 'nytimes.com': 0.80, 'wsj.com': 0.80,

            # Tech and Professional
            'github.com': 0.75, 'stackoverflow.com': 0.75, 'medium.com': 0.70,
            'techcrunch.com': 0.70, 'wired.com': 0.70, 'arstechnica.com': 0.70,

            # Wikipedia and Reference
            'wikipedia.org': 0.75, 'britannica.com': 0.80,

            # General web
            'com': 0.50, 'org': 0.55, 'net': 0.45
        }

    def score_source(self, url: str, title: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive source credibility scoring"""
        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        scores = {
            "domain_authority": self._score_domain_authority(domain),
            "content_quality": self._score_content_quality(content),
            "citation_presence": self._score_citations(content),
            "freshness": self._score_freshness(metadata.get("timestamp", "")),
            "objectivity": self._score_objectivity(content),
            "depth": self._score_depth(content),
        }

        # Calculate weighted overall score
        weights = {
            "domain_authority": 0.30,
            "content_quality": 0.25,
            "citation_presence": 0.15,
            "freshness": 0.10,
            "objectivity": 0.10,
            "depth": 0.10
        }

        overall_score = sum(scores[key] * weights[key] for key in scores)

        return {
            "overall_credibility": round(overall_score, 3),
            "breakdown": scores,
            "trust_level": self._get_trust_level(overall_score),
            "domain": domain,
            "recommendations": self._get_recommendations(scores)
        }

    def _score_domain_authority(self, domain: str) -> float:
        """Score based on domain authority"""
        # Check exact domain match
        if domain in self.trusted_domains:
            return self.trusted_domains[domain]

        # Check TLD
        tld = domain.split('.')[-1]
        if tld in self.trusted_domains:
            return self.trusted_domains[tld]

        # Check if it's an educational domain
        if '.edu' in domain:
            return 0.95
        elif '.gov' in domain:
            return 0.90
        elif '.org' in domain:
            return 0.55

        return 0.50  # Default score

    def _score_content_quality(self, content: str) -> float:
        """Score based on content quality indicators"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)

        if not words:
            return 0.0

        score = 0.5  # Base score

        # Length indicates depth
        word_count = len(words)
        if word_count > 500:
            score += 0.1
        if word_count > 1000:
            score += 0.1

        # Proper grammar indicators (capitalized sentences)
        capitalized_sentences = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        if len(sentences) > 0:
            grammar_score = capitalized_sentences / len(sentences)
            score += grammar_score * 0.15

        # Presence of data/statistics
        if re.search(r'\d+%|\d+\.\d+|statistics|data|study|research', content.lower()):
            score += 0.15

        return min(1.0, score)

    def _score_citations(self, content: str) -> float:
        """Score based on presence of citations and references"""
        citation_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\(\d{4}\)',  # (2024)
            r'et al\.',  # Academic citations
            r'according to',  # Source attribution
            r'source:',  # Explicit sourcing
            r'https?://',  # URLs as references
        ]

        citation_count = 0
        for pattern in citation_patterns:
            citation_count += len(re.findall(pattern, content, re.IGNORECASE))

        # Normalize by content length
        words = len(content.split())
        if words == 0:
            return 0.0

        citation_density = citation_count / (words / 100)  # Citations per 100 words
        return min(1.0, citation_density / 5)  # Cap at 5 citations per 100 words

    def _score_freshness(self, timestamp: str) -> float:
        """Score based on content freshness"""
        if not timestamp:
            return 0.5  # Unknown age

        try:
            pub_date = datetime.fromisoformat(timestamp)
            age_days = (datetime.now() - pub_date).days

            if age_days < 30:
                return 1.0
            elif age_days < 90:
                return 0.9
            elif age_days < 180:
                return 0.8
            elif age_days < 365:
                return 0.7
            else:
                return 0.6
        except:
            return 0.5

    def _score_objectivity(self, content: str) -> float:
        """Score based on objectivity vs opinion"""
        content_lower = content.lower()

        # Opinion indicators
        opinion_words = ['i think', 'i believe', 'in my opinion', 'i feel', 'seems like',
                        'probably', 'maybe', 'might be', 'could be']
        opinion_count = sum(content_lower.count(word) for word in opinion_words)

        # Factual indicators
        factual_words = ['study', 'research', 'data', 'evidence', 'found', 'showed',
                        'demonstrated', 'according to', 'statistics', 'measured']
        factual_count = sum(content_lower.count(word) for word in factual_words)

        words = len(content.split())
        if words == 0:
            return 0.5

        opinion_density = opinion_count / (words / 100)
        factual_density = factual_count / (words / 100)

        # Higher factual, lower opinion = more objective
        objectivity = 0.5 + (factual_density * 0.1) - (opinion_density * 0.1)
        return max(0.0, min(1.0, objectivity))

    def _score_depth(self, content: str) -> float:
        """Score based on content depth and detail"""
        words = content.split()

        if len(words) < 100:
            return 0.2
        elif len(words) < 300:
            return 0.4
        elif len(words) < 500:
            return 0.6
        elif len(words) < 1000:
            return 0.8
        else:
            return 1.0

    def _get_trust_level(self, score: float) -> str:
        """Convert score to human-readable trust level"""
        if score >= 0.85:
            return "Very High"
        elif score >= 0.70:
            return "High"
        elif score >= 0.55:
            return "Moderate"
        elif score >= 0.40:
            return "Low"
        else:
            return "Very Low"

    def _get_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Provide recommendations based on scores"""
        recommendations = []

        if scores["domain_authority"] < 0.6:
            recommendations.append("Cross-reference with more authoritative sources")
        if scores["citation_presence"] < 0.3:
            recommendations.append("Look for sources with more citations")
        if scores["freshness"] < 0.7:
            recommendations.append("Check for more recent information")
        if scores["objectivity"] < 0.5:
            recommendations.append("Consider potential bias in this source")
        if scores["depth"] < 0.5:
            recommendations.append("Seek more detailed coverage of the topic")

        if not recommendations:
            recommendations.append("Source appears credible and comprehensive")

        return recommendations


class KnowledgeGraphGenerator:
    """Extract entities and relationships to build knowledge graphs"""

    def __init__(self):
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: List[Dict[str, Any]] = []

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        entities = []

        # Extract proper nouns (capitalized phrases)
        entity_patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

        # Count frequencies
        entity_freq = Counter(entity_patterns)

        # Filter and categorize
        for entity, freq in entity_freq.items():
            if freq >= 2 or len(entity.split()) > 1:  # At least 2 mentions or multi-word
                entity_type = self._categorize_entity(entity)
                entities.append({
                    "name": entity,
                    "type": entity_type,
                    "mentions": freq,
                    "id": hashlib.md5(entity.encode()).hexdigest()[:8]
                })

        return entities

    def _categorize_entity(self, entity: str) -> str:
        """Simple entity type classification"""
        # Location indicators
        if any(word in entity for word in ['University', 'Institute', 'Center', 'Laboratory']):
            return "Organization"
        elif any(word in entity for word in ['Dr.', 'Professor', 'President', 'CEO']):
            return "Person"
        elif any(word in entity for word in ['United States', 'China', 'Europe', 'Asia']):
            return "Location"
        elif re.search(r'\d{4}', entity):  # Contains year
            return "Event"
        elif entity.endswith('Inc') or entity.endswith('Corp') or entity.endswith('LLC'):
            return "Organization"
        else:
            # Default categorization based on position and context
            words = entity.split()
            if len(words) == 1:
                return "Concept"
            else:
                return "Organization"  # Multi-word entities often organizations

    def extract_relationships(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities"""
        relationships = []

        # Create entity lookup
        entity_names = [e["name"] for e in entities]

        # Find co-occurrences in sentences
        sentences = re.split(r'[.!?]+', text)

        for sentence in sentences:
            # Find entities in this sentence
            present_entities = [e for e in entity_names if e in sentence]

            # Create relationships between co-occurring entities
            if len(present_entities) >= 2:
                for i in range(len(present_entities)):
                    for j in range(i + 1, len(present_entities)):
                        relationship = self._detect_relationship_type(sentence, present_entities[i], present_entities[j])
                        relationships.append({
                            "entity1": present_entities[i],
                            "entity2": present_entities[j],
                            "relationship": relationship,
                            "context": sentence.strip()[:100]  # First 100 chars
                        })

        return relationships

    def _detect_relationship_type(self, sentence: str, entity1: str, entity2: str) -> str:
        """Detect the type of relationship between entities"""
        sentence_lower = sentence.lower()

        if any(word in sentence_lower for word in ['founded', 'created', 'established', 'started']):
            return "founded_by"
        elif any(word in sentence_lower for word in ['works at', 'employed by', 'member of']):
            return "affiliated_with"
        elif any(word in sentence_lower for word in ['located in', 'based in', 'from']):
            return "located_in"
        elif any(word in sentence_lower for word in ['researches', 'studies', 'investigates']):
            return "researches"
        elif any(word in sentence_lower for word in ['collaborated with', 'worked with', 'partnered with']):
            return "collaborates_with"
        else:
            return "related_to"

    def build_graph(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a knowledge graph from multiple documents"""
        all_entities = []
        all_relationships = []

        for doc in documents:
            text = f"{doc.get('title', '')} {doc.get('content', '')}"
            entities = self.extract_entities(text)
            relationships = self.extract_relationships(text, entities)

            all_entities.extend(entities)
            all_relationships.extend(relationships)

        # Deduplicate and merge entities
        entity_map = {}
        for entity in all_entities:
            name = entity["name"]
            if name in entity_map:
                entity_map[name]["mentions"] += entity["mentions"]
            else:
                entity_map[name] = entity

        return {
            "entities": list(entity_map.values()),
            "relationships": all_relationships,
            "stats": {
                "total_entities": len(entity_map),
                "total_relationships": len(all_relationships),
                "entity_types": Counter(e["type"] for e in entity_map.values())
            }
        }


class SmartQueryExpander:
    """Intelligent query expansion and suggestion system"""

    def __init__(self):
        self.query_history: List[str] = []
        self.synonym_map = {
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'neural networks'],
            'ml': ['machine learning', 'ai', 'predictive analytics'],
            'tech': ['technology', 'computing', 'digital', 'innovation'],
            'data': ['information', 'statistics', 'analytics', 'metrics'],
            'climate': ['environment', 'global warming', 'weather', 'sustainability'],
            'health': ['healthcare', 'medicine', 'wellness', 'medical'],
            'economy': ['economic', 'financial', 'business', 'market'],
            'research': ['study', 'investigation', 'analysis', 'examination'],
        }

    def expand_query(self, query: str) -> Dict[str, Any]:
        """Expand query with synonyms and related terms"""
        query_lower = query.lower()
        words = query_lower.split()

        expanded_terms = set([query])
        related_terms = []

        # Add synonyms
        for word in words:
            if word in self.synonym_map:
                related_terms.extend(self.synonym_map[word])
                # Create expanded queries
                for synonym in self.synonym_map[word]:
                    expanded_query = query_lower.replace(word, synonym)
                    expanded_terms.add(expanded_query)

        # Add question forms
        question_forms = self._generate_questions(query)

        # Add related searches
        related_searches = self._generate_related_searches(query)

        return {
            "original_query": query,
            "expanded_queries": list(expanded_terms),
            "related_terms": list(set(related_terms)),
            "question_forms": question_forms,
            "related_searches": related_searches,
            "search_tips": self._generate_search_tips(query)
        }

    def _generate_questions(self, query: str) -> List[str]:
        """Generate question forms of the query"""
        questions = [
            f"What is {query}?",
            f"How does {query} work?",
            f"Why is {query} important?",
            f"When was {query} discovered?",
            f"Where is {query} used?",
            f"Who invented {query}?",
        ]
        return questions

    def _generate_related_searches(self, query: str) -> List[str]:
        """Generate related search suggestions"""
        related = [
            f"{query} tutorial",
            f"{query} guide",
            f"{query} examples",
            f"best {query}",
            f"{query} vs alternatives",
            f"{query} benefits",
            f"{query} applications",
            f"latest {query} trends",
        ]
        return related

    def _generate_search_tips(self, query: str) -> List[str]:
        """Provide search optimization tips"""
        tips = [
            "Use quotes for exact phrases",
            "Add 'recent' or '2024' for latest information",
            "Try specific terms instead of general ones",
            "Combine with action words: 'how to', 'guide', 'tutorial'",
        ]
        return tips

    def suggest_follow_ups(self, query: str, results: List[Dict[str, Any]]) -> List[str]:
        """Suggest follow-up queries based on results"""
        suggestions = []

        # Extract common themes from results
        all_text = ' '.join([r.get('title', '') + ' ' + r.get('content', '')[:200] for r in results])

        # Find frequent terms
        words = re.findall(r'\b\w{4,}\b', all_text.lower())
        word_freq = Counter(words)

        # Remove query terms and common words
        query_terms = set(query.lower().split())
        common = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'their', 'there'}

        top_terms = [word for word, count in word_freq.most_common(10)
                     if word not in query_terms and word not in common]

        # Generate follow-up queries
        for term in top_terms[:5]:
            suggestions.append(f"{query} and {term}")

        return suggestions


class ResearchSessionManager:
    """Manage research sessions with SQLite persistence"""

    def __init__(self, db_path: str = "research_sessions.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        if not sqlite3:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    parameters TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')

            # Results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    title TEXT,
                    url TEXT,
                    content TEXT,
                    relevance_score REAL,
                    credibility_score REAL,
                    created_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            ''')

            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON results(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON sessions(created_at)')

            conn.commit()

    def create_session(self, query: str, parameters: Dict[str, Any]) -> str:
        """Create a new research session"""
        if not sqlite3:
            return hashlib.md5(query.encode()).hexdigest()[:12]

        session_id = hashlib.md5(f"{query}{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO sessions (id, query, created_at, updated_at, parameters)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                query,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(parameters)
            ))
            conn.commit()

        return session_id

    def save_result(self, session_id: str, result: Dict[str, Any]):
        """Save a result to a session"""
        if not sqlite3:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO results (id, session_id, title, url, content, relevance_score, credibility_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.get('id'),
                session_id,
                result.get('title'),
                result.get('url'),
                result.get('content', '')[:5000],  # Limit content size
                result.get('relevance_score', 0.0),
                result.get('credibility_score', 0.0),
                datetime.now().isoformat()
            ))

            # Update session timestamp
            cursor.execute('''
                UPDATE sessions SET updated_at = ? WHERE id = ?
            ''', (datetime.now().isoformat(), session_id))

            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a session and its results"""
        if not sqlite3:
            return None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get session info
            cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
            session_row = cursor.fetchone()

            if not session_row:
                return None

            # Get results
            cursor.execute('SELECT * FROM results WHERE session_id = ?', (session_id,))
            result_rows = cursor.fetchall()

            return {
                "session_id": session_row[0],
                "query": session_row[1],
                "created_at": session_row[2],
                "updated_at": session_row[3],
                "parameters": json.loads(session_row[4]) if session_row[4] else {},
                "status": session_row[5],
                "results_count": len(result_rows)
            }

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent sessions"""
        if not sqlite3:
            return []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, query, created_at, updated_at, status,
                       (SELECT COUNT(*) FROM results WHERE session_id = sessions.id) as result_count
                FROM sessions
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    "session_id": row[0],
                    "query": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                    "status": row[4],
                    "results_count": row[5]
                })

            return sessions


class IntelligenceEngine:
    """Main intelligence engine combining all advanced features"""

    def __init__(self):
        self.semantic_search = SemanticSearchEngine()
        self.credibility_scorer = SourceCredibilityScorer()
        self.knowledge_graph = KnowledgeGraphGenerator()
        self.query_expander = SmartQueryExpander()
        self.session_manager = ResearchSessionManager()

    def analyze_comprehensive(self, results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Comprehensive analysis using all intelligence features"""
        # Build semantic search index
        for result in results:
            self.semantic_search.add_document(
                result.get('id', ''),
                result.get('title', ''),
                result.get('content', '')
            )
        self.semantic_search.build_index()

        # Score credibility
        credibility_scores = []
        for result in results:
            score = self.credibility_scorer.score_source(
                result.get('url', ''),
                result.get('title', ''),
                result.get('content', ''),
                result.get('metadata', {})
            )
            credibility_scores.append(score)

        # Build knowledge graph
        graph = self.knowledge_graph.build_graph(results)

        # Expand query
        expanded = self.query_expander.expand_query(query)

        # Suggest follow-ups
        follow_ups = self.query_expander.suggest_follow_ups(query, results)

        return {
            "semantic_search_ready": True,
            "credibility_analysis": {
                "average_score": sum(s["overall_credibility"] for s in credibility_scores) / len(credibility_scores) if credibility_scores else 0,
                "high_credibility_count": sum(1 for s in credibility_scores if s["overall_credibility"] >= 0.7),
                "low_credibility_count": sum(1 for s in credibility_scores if s["overall_credibility"] < 0.5),
                "details": credibility_scores
            },
            "knowledge_graph": graph,
            "query_expansion": expanded,
            "follow_up_suggestions": follow_ups,
            "intelligence_metrics": {
                "total_entities": graph["stats"]["total_entities"],
                "total_relationships": graph["stats"]["total_relationships"],
                "semantic_vectors": len(self.semantic_search.doc_vectors),
                "vocabulary_size": len(self.semantic_search.vocabulary)
            }
        }
