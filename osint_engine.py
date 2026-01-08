"""
OSINT Engine - Next-Generation Open Source Intelligence
Cutting-edge techniques for advanced research and analysis
"""

import re
import json
from typing import List, Dict, Any, Set, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin
import hashlib


class SocialNetworkAnalyzer:
    """Advanced social network analysis and mapping"""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.communities: List[Set[str]] = []

    def add_entity(self, entity_id: str, entity_type: str, metadata: Dict[str, Any]):
        """Add a node to the network"""
        self.nodes[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "metadata": metadata,
            "connections": set(),
            "influence_score": 0.0
        }

    def add_connection(self, entity1: str, entity2: str, relationship_type: str, weight: float = 1.0):
        """Add an edge between nodes"""
        if entity1 not in self.nodes or entity2 not in self.nodes:
            return

        self.edges.append({
            "source": entity1,
            "target": entity2,
            "type": relationship_type,
            "weight": weight
        })

        self.nodes[entity1]["connections"].add(entity2)
        self.nodes[entity2]["connections"].add(entity1)

    def calculate_influence(self) -> Dict[str, float]:
        """Calculate influence scores using PageRank-like algorithm"""
        if not self.nodes:
            return {}

        # Initialize scores
        scores = {node_id: 1.0 for node_id in self.nodes}
        damping = 0.85
        iterations = 20

        for _ in range(iterations):
            new_scores = {}
            for node_id in self.nodes:
                # Get incoming connections
                incoming = [e for e in self.edges if e["target"] == node_id]

                score = (1 - damping)
                for edge in incoming:
                    source = edge["source"]
                    out_degree = len(self.nodes[source]["connections"])
                    if out_degree > 0:
                        score += damping * (scores[source] / out_degree) * edge["weight"]

                new_scores[node_id] = score

            scores = new_scores

        # Normalize scores
        max_score = max(scores.values()) if scores else 1.0
        for node_id in scores:
            self.nodes[node_id]["influence_score"] = scores[node_id] / max_score

        return scores

    def detect_communities(self) -> List[Set[str]]:
        """Detect communities using simple clustering"""
        visited = set()
        communities = []

        def dfs(node, community):
            if node in visited:
                return
            visited.add(node)
            community.add(node)

            for connected in self.nodes[node]["connections"]:
                if connected not in visited:
                    dfs(connected, community)

        for node_id in self.nodes:
            if node_id not in visited:
                community = set()
                dfs(node_id, community)
                if len(community) > 1:  # Only keep communities with multiple members
                    communities.append(community)

        self.communities = communities
        return communities

    def get_central_nodes(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """Get most influential/central nodes"""
        self.calculate_influence()

        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1]["influence_score"],
            reverse=True
        )

        return [
            {
                "id": node_id,
                "type": node[1]["type"],
                "influence_score": node[1]["influence_score"],
                "connections_count": len(node[1]["connections"]),
                "metadata": node[1]["metadata"]
            }
            for node_id, node in sorted_nodes[:top_k]
        ]

    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        if not self.nodes:
            return {}

        total_connections = sum(len(node["connections"]) for node in self.nodes.values())
        avg_connections = total_connections / len(self.nodes) if self.nodes else 0

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "average_connections": round(avg_connections, 2),
            "total_communities": len(self.communities),
            "network_density": len(self.edges) / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0,
            "node_types": Counter(node["type"] for node in self.nodes.values())
        }


class DigitalFootprintTracker:
    """Track and analyze digital footprints across platforms"""

    def __init__(self):
        self.footprints: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.platforms = ['twitter', 'linkedin', 'github', 'medium', 'reddit', 'stackoverflow']

    def add_footprint(self, entity: str, platform: str, data: Dict[str, Any]):
        """Record a digital footprint"""
        footprint = {
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "fingerprint": self._generate_fingerprint(data)
        }
        self.footprints[entity].append(footprint)

    def _generate_fingerprint(self, data: Dict[str, Any]) -> str:
        """Generate unique fingerprint from data"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def analyze_presence(self, entity: str) -> Dict[str, Any]:
        """Analyze digital presence across platforms"""
        if entity not in self.footprints:
            return {"error": "Entity not found"}

        footprints = self.footprints[entity]
        platforms = Counter(f["platform"] for f in footprints)

        return {
            "entity": entity,
            "total_footprints": len(footprints),
            "platforms_active": len(platforms),
            "platform_distribution": dict(platforms),
            "first_seen": min(f["timestamp"] for f in footprints),
            "last_seen": max(f["timestamp"] for f in footprints),
            "activity_score": self._calculate_activity_score(footprints),
            "cross_platform_patterns": self._detect_patterns(footprints)
        }

    def _calculate_activity_score(self, footprints: List[Dict[str, Any]]) -> float:
        """Calculate activity score based on frequency and recency"""
        if not footprints:
            return 0.0

        # Recency score
        latest = datetime.fromisoformat(max(f["timestamp"] for f in footprints))
        days_ago = (datetime.now() - latest).days
        recency_score = max(0, 1 - (days_ago / 30))  # Decay over 30 days

        # Frequency score
        frequency_score = min(1.0, len(footprints) / 100)  # Cap at 100 footprints

        return round((recency_score * 0.6 + frequency_score * 0.4), 3)

    def _detect_patterns(self, footprints: List[Dict[str, Any]]) -> List[str]:
        """Detect patterns in cross-platform activity"""
        patterns = []

        # Check for simultaneous platform usage
        platforms = Counter(f["platform"] for f in footprints)
        if len(platforms) >= 3:
            patterns.append("Multi-platform presence detected")

        # Check for consistent timing
        timestamps = [datetime.fromisoformat(f["timestamp"]) for f in footprints]
        if len(timestamps) > 1:
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
            avg_diff = sum(time_diffs) / len(time_diffs)
            if avg_diff < 3600:  # Less than 1 hour average
                patterns.append("High-frequency activity pattern")

        return patterns

    def find_connections(self, entity1: str, entity2: str) -> Dict[str, Any]:
        """Find connections between two entities"""
        if entity1 not in self.footprints or entity2 not in self.footprints:
            return {"connections": []}

        fp1 = self.footprints[entity1]
        fp2 = self.footprints[entity2]

        # Find common platforms
        platforms1 = set(f["platform"] for f in fp1)
        platforms2 = set(f["platform"] for f in fp2)
        common_platforms = platforms1 & platforms2

        # Find temporal overlaps
        overlaps = []
        for f1 in fp1:
            for f2 in fp2:
                time1 = datetime.fromisoformat(f1["timestamp"])
                time2 = datetime.fromisoformat(f2["timestamp"])
                if abs((time1 - time2).total_seconds()) < 3600:  # Within 1 hour
                    overlaps.append({
                        "platform1": f1["platform"],
                        "platform2": f2["platform"],
                        "time_difference_seconds": abs((time1 - time2).total_seconds())
                    })

        return {
            "common_platforms": list(common_platforms),
            "temporal_overlaps": len(overlaps),
            "connection_strength": len(common_platforms) * 0.5 + min(len(overlaps) * 0.1, 0.5)
        }


class TimelineAnalyzer:
    """Advanced timeline analysis and event correlation"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def add_event(self, event_type: str, timestamp: str, data: Dict[str, Any]):
        """Add an event to the timeline"""
        self.events.append({
            "type": event_type,
            "timestamp": timestamp,
            "data": data,
            "datetime": datetime.fromisoformat(timestamp) if timestamp else None
        })

    def build_timeline(self) -> List[Dict[str, Any]]:
        """Build chronological timeline"""
        sorted_events = sorted(
            [e for e in self.events if e["datetime"]],
            key=lambda x: x["datetime"]
        )

        timeline = []
        for event in sorted_events:
            timeline.append({
                "timestamp": event["timestamp"],
                "type": event["type"],
                "description": event["data"].get("description", ""),
                "metadata": event["data"]
            })

        return timeline

    def detect_patterns(self) -> Dict[str, Any]:
        """Detect temporal patterns and correlations"""
        if len(self.events) < 2:
            return {"patterns": []}

        sorted_events = sorted(
            [e for e in self.events if e["datetime"]],
            key=lambda x: x["datetime"]
        )

        patterns = {
            "event_clusters": self._find_event_clusters(sorted_events),
            "recurring_patterns": self._find_recurring_patterns(sorted_events),
            "anomalies": self._find_anomalies(sorted_events),
            "peak_activity_times": self._find_peak_times(sorted_events)
        }

        return patterns

    def _find_event_clusters(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find clusters of events in time"""
        clusters = []
        cluster_threshold = timedelta(hours=24)  # Events within 24 hours

        current_cluster = [events[0]] if events else []

        for i in range(1, len(events)):
            time_diff = events[i]["datetime"] - events[i-1]["datetime"]

            if time_diff <= cluster_threshold:
                current_cluster.append(events[i])
            else:
                if len(current_cluster) >= 3:  # Minimum 3 events for a cluster
                    clusters.append({
                        "start": current_cluster[0]["timestamp"],
                        "end": current_cluster[-1]["timestamp"],
                        "event_count": len(current_cluster),
                        "event_types": [e["type"] for e in current_cluster]
                    })
                current_cluster = [events[i]]

        return clusters

    def _find_recurring_patterns(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find recurring patterns in event types"""
        if len(events) < 3:
            return []

        # Look for repeated sequences
        event_types = [e["type"] for e in events]
        patterns = []

        for length in range(2, min(5, len(event_types) // 2)):
            for i in range(len(event_types) - length):
                sequence = tuple(event_types[i:i+length])
                # Check if this sequence appears again
                for j in range(i + length, len(event_types) - length):
                    if tuple(event_types[j:j+length]) == sequence:
                        patterns.append({
                            "pattern": list(sequence),
                            "first_occurrence": events[i]["timestamp"],
                            "second_occurrence": events[j]["timestamp"],
                            "pattern_length": length
                        })
                        break

        return patterns

    def _find_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find anomalous gaps or bursts in timeline"""
        if len(events) < 3:
            return []

        time_diffs = [(events[i+1]["datetime"] - events[i]["datetime"]).total_seconds()
                     for i in range(len(events)-1)]

        avg_diff = sum(time_diffs) / len(time_diffs)
        std_dev = (sum((x - avg_diff) ** 2 for x in time_diffs) / len(time_diffs)) ** 0.5

        anomalies = []
        for i, diff in enumerate(time_diffs):
            if abs(diff - avg_diff) > 2 * std_dev:  # 2 standard deviations
                anomalies.append({
                    "type": "gap" if diff > avg_diff else "burst",
                    "timestamp": events[i]["timestamp"],
                    "duration_seconds": diff,
                    "deviation_from_normal": round((diff - avg_diff) / std_dev, 2)
                })

        return anomalies

    def _find_peak_times(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find peak activity times"""
        if not events:
            return {}

        hours = [e["datetime"].hour for e in events if e["datetime"]]
        days = [e["datetime"].strftime("%A") for e in events if e["datetime"]]

        hour_counts = Counter(hours)
        day_counts = Counter(days)

        return {
            "peak_hour": hour_counts.most_common(1)[0] if hour_counts else None,
            "peak_day": day_counts.most_common(1)[0] if day_counts else None,
            "hourly_distribution": dict(hour_counts),
            "daily_distribution": dict(day_counts)
        }


class SentimentTrendAnalyzer:
    """Track sentiment trends over time"""

    def __init__(self):
        self.data_points: List[Dict[str, Any]] = []

    def add_sentiment_data(self, timestamp: str, sentiment: str, content: str, source: str):
        """Add a sentiment data point"""
        sentiment_score = {
            'positive': 1.0,
            'neutral': 0.0,
            'negative': -1.0
        }.get(sentiment.lower(), 0.0)

        self.data_points.append({
            "timestamp": timestamp,
            "datetime": datetime.fromisoformat(timestamp),
            "sentiment": sentiment,
            "score": sentiment_score,
            "content": content[:200],  # First 200 chars
            "source": source
        })

    def analyze_trends(self, time_window_days: int = 30) -> Dict[str, Any]:
        """Analyze sentiment trends"""
        if not self.data_points:
            return {}

        sorted_points = sorted(self.data_points, key=lambda x: x["datetime"])

        # Overall sentiment
        avg_sentiment = sum(p["score"] for p in sorted_points) / len(sorted_points)

        # Time-based trends
        recent_cutoff = datetime.now() - timedelta(days=time_window_days)
        recent_points = [p for p in sorted_points if p["datetime"] >= recent_cutoff]

        recent_avg = sum(p["score"] for p in recent_points) / len(recent_points) if recent_points else 0

        # Detect sentiment shifts
        shifts = self._detect_sentiment_shifts(sorted_points)

        # Source breakdown
        source_sentiments = defaultdict(list)
        for point in sorted_points:
            source_sentiments[point["source"]].append(point["score"])

        source_avg = {
            source: sum(scores) / len(scores)
            for source, scores in source_sentiments.items()
        }

        return {
            "overall_sentiment": self._score_to_label(avg_sentiment),
            "overall_score": round(avg_sentiment, 3),
            "recent_sentiment": self._score_to_label(recent_avg),
            "recent_score": round(recent_avg, 3),
            "trend": "improving" if recent_avg > avg_sentiment else "declining" if recent_avg < avg_sentiment else "stable",
            "sentiment_shifts": shifts,
            "source_breakdown": {k: round(v, 3) for k, v in source_avg.items()},
            "data_points_analyzed": len(sorted_points)
        }

    def _score_to_label(self, score: float) -> str:
        """Convert score to label"""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"

    def _detect_sentiment_shifts(self, sorted_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect significant sentiment shifts"""
        if len(sorted_points) < 10:
            return []

        shifts = []
        window_size = max(5, len(sorted_points) // 10)

        for i in range(window_size, len(sorted_points) - window_size):
            before_avg = sum(p["score"] for p in sorted_points[i-window_size:i]) / window_size
            after_avg = sum(p["score"] for p in sorted_points[i:i+window_size]) / window_size

            diff = after_avg - before_avg
            if abs(diff) > 0.5:  # Significant shift
                shifts.append({
                    "timestamp": sorted_points[i]["timestamp"],
                    "direction": "positive" if diff > 0 else "negative",
                    "magnitude": round(abs(diff), 3),
                    "before_sentiment": self._score_to_label(before_avg),
                    "after_sentiment": self._score_to_label(after_avg)
                })

        return shifts


class GeospatialAnalyzer:
    """Geospatial intelligence and location analysis"""

    def __init__(self):
        self.locations: List[Dict[str, Any]] = []

    def add_location(self, location_name: str, coordinates: Optional[Tuple[float, float]] = None,
                    metadata: Dict[str, Any] = None):
        """Add a location reference"""
        self.locations.append({
            "name": location_name,
            "coordinates": coordinates,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })

    def extract_locations_from_text(self, text: str) -> List[str]:
        """Extract location references from text"""
        # Common location patterns
        location_patterns = [
            r'\b(?:in|at|from|to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in New York"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:city|country|state|region)',  # "New York city"
            r'\b(?:United States|China|India|Russia|Japan|Germany|France|Brazil|UK)\b',  # Major countries
        ]

        locations = set()
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            locations.update(matches if isinstance(matches, list) else [matches])

        return list(locations)

    def analyze_location_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in location references"""
        if not self.locations:
            return {}

        location_freq = Counter(loc["name"] for loc in self.locations)

        return {
            "unique_locations": len(location_freq),
            "total_references": len(self.locations),
            "top_locations": location_freq.most_common(10),
            "geographic_diversity_score": len(location_freq) / len(self.locations) if self.locations else 0
        }


class PatternRecognitionEngine:
    """Advanced pattern recognition across data"""

    def __init__(self):
        self.patterns: List[Dict[str, Any]] = []

    def detect_numerical_patterns(self, numbers: List[float]) -> Dict[str, Any]:
        """Detect patterns in numerical data"""
        if len(numbers) < 3:
            return {}

        patterns = {
            "trend": self._detect_trend(numbers),
            "cycles": self._detect_cycles(numbers),
            "anomalies": self._detect_numerical_anomalies(numbers),
            "statistics": {
                "mean": sum(numbers) / len(numbers),
                "median": sorted(numbers)[len(numbers) // 2],
                "std_dev": (sum((x - sum(numbers)/len(numbers)) ** 2 for x in numbers) / len(numbers)) ** 0.5,
                "range": max(numbers) - min(numbers)
            }
        }

        return patterns

    def _detect_trend(self, numbers: List[float]) -> str:
        """Detect overall trend"""
        if len(numbers) < 2:
            return "insufficient_data"

        increases = sum(1 for i in range(1, len(numbers)) if numbers[i] > numbers[i-1])
        decreases = sum(1 for i in range(1, len(numbers)) if numbers[i] < numbers[i-1])

        if increases > len(numbers) * 0.6:
            return "increasing"
        elif decreases > len(numbers) * 0.6:
            return "decreasing"
        else:
            return "stable"

    def _detect_cycles(self, numbers: List[float]) -> List[int]:
        """Detect cyclic patterns"""
        cycles = []

        for period in range(2, min(len(numbers) // 2, 20)):
            is_cyclic = True
            for i in range(len(numbers) - period):
                if abs(numbers[i] - numbers[i + period]) > 0.1 * abs(numbers[i]):
                    is_cyclic = False
                    break

            if is_cyclic:
                cycles.append(period)

        return cycles

    def _detect_numerical_anomalies(self, numbers: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in numerical data"""
        if len(numbers) < 3:
            return []

        mean = sum(numbers) / len(numbers)
        std_dev = (sum((x - mean) ** 2 for x in numbers) / len(numbers)) ** 0.5

        anomalies = []
        for i, num in enumerate(numbers):
            z_score = abs((num - mean) / std_dev) if std_dev > 0 else 0
            if z_score > 2:  # 2 standard deviations
                anomalies.append({
                    "index": i,
                    "value": num,
                    "z_score": round(z_score, 2),
                    "deviation": "high" if num > mean else "low"
                })

        return anomalies


class OSINTEngine:
    """Main OSINT engine combining all advanced techniques"""

    def __init__(self):
        self.social_network = SocialNetworkAnalyzer()
        self.footprint_tracker = DigitalFootprintTracker()
        self.timeline = TimelineAnalyzer()
        self.sentiment = SentimentTrendAnalyzer()
        self.geospatial = GeospatialAnalyzer()
        self.pattern_recognition = PatternRecognitionEngine()

    def comprehensive_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive OSINT analysis"""
        results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_analyzed": {
                "sources": data.get("source_count", 0),
                "entities": data.get("entity_count", 0),
                "time_span": data.get("time_span", "unknown")
            },
            "osint_insights": {}
        }

        # Add each analysis component
        if "network_data" in data:
            results["osint_insights"]["social_network"] = self.social_network.get_network_stats()

        if "timeline_events" in data:
            results["osint_insights"]["timeline_patterns"] = self.timeline.detect_patterns()

        if "sentiment_data" in data:
            results["osint_insights"]["sentiment_trends"] = self.sentiment.analyze_trends()

        if "location_data" in data:
            results["osint_insights"]["geospatial"] = self.geospatial.analyze_location_patterns()

        return results

    def get_intelligence_score(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall intelligence score for research"""
        if not results:
            return {"score": 0.0, "quality": "no_data"}

        # Aggregate scores from different dimensions
        source_diversity = len(set(r.get("source", "") for r in results))
        avg_relevance = sum(r.get("relevance_score", 0) for r in results) / len(results)

        # Content depth
        avg_content_length = sum(len(r.get("content", "")) for r in results) / len(results)
        depth_score = min(1.0, avg_content_length / 1000)  # Normalize to 1000 chars

        # Temporal diversity
        timestamps = [r.get("timestamp") for r in results if r.get("timestamp")]
        temporal_score = len(set(t[:10] for t in timestamps)) / 30 if timestamps else 0.5  # Unique days

        # Combined intelligence score
        intelligence_score = (
            source_diversity * 0.25 +
            avg_relevance * 0.35 +
            depth_score * 0.20 +
            temporal_score * 0.20
        )

        quality_labels = [
            (0.8, "excellent"),
            (0.6, "good"),
            (0.4, "moderate"),
            (0.2, "fair"),
            (0.0, "poor")
        ]

        quality = next(label for threshold, label in quality_labels if intelligence_score >= threshold)

        return {
            "intelligence_score": round(intelligence_score, 3),
            "quality": quality,
            "breakdown": {
                "source_diversity": source_diversity,
                "average_relevance": round(avg_relevance, 3),
                "content_depth": round(depth_score, 3),
                "temporal_diversity": round(temporal_score, 3)
            },
            "recommendations": self._get_intelligence_recommendations(intelligence_score)
        }

    def _get_intelligence_recommendations(self, score: float) -> List[str]:
        """Get recommendations based on intelligence score"""
        recommendations = []

        if score < 0.3:
            recommendations.append("Expand search to include more diverse sources")
            recommendations.append("Increase query depth and detail level")
            recommendations.append("Consider using query expansion techniques")
        elif score < 0.6:
            recommendations.append("Add more specialized sources for better depth")
            recommendations.append("Cross-reference findings with authoritative sources")
        else:
            recommendations.append("Intelligence quality is high - consider deeper analysis")
            recommendations.append("Look for patterns and relationships in the data")

        return recommendations
