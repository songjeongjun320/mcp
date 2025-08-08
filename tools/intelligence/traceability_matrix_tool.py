"""
ATOMS.TECH Intelligent Traceability Matrix Generator
Phase 3 - Custom Requirements Intelligence

Purpose: Automated traceability matrix generation with semantic link analysis
Expected Benefits:
- 80% reduction in traceability matrix generation time
- Automatic semantic similarity-based linking
- Network analysis for traceability visualization
- Change impact analysis with dependency mapping
- Automated gap identification and resolution
"""

import json
import logging
import os
import asyncio
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import itertools

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import networkx as nx
from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import (
    setup_intelligence_logging,
    get_cache,
    INTELLIGENCE_CONFIG,
    AI_MODELS,
    PERFORMANCE_THRESHOLDS
)

logger = setup_intelligence_logging('traceability_matrix')

@dataclass
class TraceabilityLink:
    """Data class for traceability relationships"""
    source_id: str
    target_id: str
    source_type: str
    target_type: str
    link_type: str
    confidence: float
    strength: float
    rationale: str
    created_at: datetime
    validated: bool = False

@dataclass
class RequirementNode:
    """Data class for requirement nodes in traceability network"""
    id: str
    text: str
    type: str
    priority: str
    status: str
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = None

@dataclass
class TraceabilityGap:
    """Data class for identified traceability gaps"""
    gap_id: str
    gap_type: str
    description: str
    severity: str
    affected_requirements: List[str]
    suggested_links: List[TraceabilityLink]
    resolution_priority: int

class IntelligentTraceabilityMatrix:
    """AI-powered traceability matrix generator with semantic analysis"""
    
    def __init__(self):
        self.enabled = INTELLIGENCE_CONFIG['enabled']
        self.cache = get_cache('traceability_matrix')
        self.embedding_model = None
        self.vectorizer = None
        self.similarity_threshold = 0.3
        self.confidence_threshold = INTELLIGENCE_CONFIG['recommendation_confidence_threshold']
        
        # Link type configurations
        self.link_types = {
            'derived_from': {
                'weight': 1.0,
                'description': 'Target is derived from source',
                'reverse': 'derives_to'
            },
            'depends_on': {
                'weight': 0.8,
                'description': 'Source depends on target',
                'reverse': 'supports'
            },
            'implements': {
                'weight': 0.9,
                'description': 'Source implements target',
                'reverse': 'implemented_by'
            },
            'tests': {
                'weight': 0.7,
                'description': 'Source tests target',
                'reverse': 'tested_by'
            },
            'conflicts_with': {
                'weight': 0.6,
                'description': 'Source conflicts with target',
                'reverse': 'conflicts_with'
            },
            'related_to': {
                'weight': 0.5,
                'description': 'Source is related to target',
                'reverse': 'related_to'
            }
        }
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize AI models for traceability analysis"""
        try:
            # Load sentence transformer for semantic similarity
            model_name = INTELLIGENCE_CONFIG['embedding_model']
            self.embedding_model = SentenceTransformer(model_name)
            
            # Initialize TF-IDF vectorizer for keyword analysis
            self.vectorizer = TfidfVectorizer(
                max_features=3000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            logger.info("Traceability models initialized successfully")
            
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            self.enabled = False
    
    async def generate_traceability_matrix(
        self,
        organization_id: str,
        requirements: List[Dict[str, Any]],
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive traceability matrix with AI analysis
        
        Args:
            organization_id: Organization identifier
            requirements: List of requirement dictionaries
            options: Configuration options for matrix generation
            
        Returns:
            Dict containing traceability matrix and analysis results
        """
        
        if not self.enabled:
            return {
                "success": False,
                "error": "Traceability AI disabled",
                "fallback": "Manual matrix creation available"
            }
        
        start_time = datetime.now()
        options = options or {}
        
        try:
            # Generate cache key
            req_hash = self._generate_requirements_hash(requirements)
            cache_key = f"traceability_{organization_id}_{req_hash}_{hash(str(options))}"
            
            # Check cache
            cached_result = self.cache.get(cache_key)
            if cached_result and not options.get('force_regenerate', False):
                logger.info(f"Using cached traceability matrix for {organization_id}")
                return cached_result
            
            # Convert requirements to nodes
            nodes = self._create_requirement_nodes(requirements)
            
            # Generate embeddings for semantic analysis
            await self._generate_embeddings(nodes)
            
            # Discover traceability links
            links = await self._discover_traceability_links(nodes, options)
            
            # Build traceability network
            network = self._build_traceability_network(nodes, links)
            
            # Analyze network properties
            network_analysis = self._analyze_network_properties(network, nodes, links)
            
            # Identify traceability gaps
            gaps = self._identify_traceability_gaps(nodes, links, network)
            
            # Generate matrix visualization data
            matrix_data = self._generate_matrix_data(nodes, links)
            
            # Calculate impact analysis
            impact_analysis = self._calculate_change_impact(nodes, links, network)
            
            # Generate improvement recommendations
            recommendations = self._generate_traceability_recommendations(
                nodes, links, gaps, network_analysis
            )
            
            # Compile comprehensive results
            results = {
                "success": True,
                "organization_id": organization_id,
                "traceability_summary": {
                    "total_requirements": len(nodes),
                    "total_links": len(links),
                    "link_types": {
                        link_type: len([l for l in links if l.link_type == link_type])
                        for link_type in self.link_types.keys()
                    },
                    "coverage_percentage": self._calculate_coverage_percentage(nodes, links),
                    "network_density": network_analysis.get('density', 0.0),
                    "gaps_identified": len(gaps)
                },
                "traceability_matrix": matrix_data,
                "discovered_links": [
                    {
                        "source_id": link.source_id,
                        "target_id": link.target_id,
                        "source_type": link.source_type,
                        "target_type": link.target_type,
                        "link_type": link.link_type,
                        "confidence": link.confidence,
                        "strength": link.strength,
                        "rationale": link.rationale,
                        "validated": link.validated
                    }
                    for link in links
                ],
                "network_analysis": network_analysis,
                "traceability_gaps": [
                    {
                        "gap_id": gap.gap_id,
                        "gap_type": gap.gap_type,
                        "description": gap.description,
                        "severity": gap.severity,
                        "affected_requirements": gap.affected_requirements,
                        "suggested_links": [
                            {
                                "source_id": link.source_id,
                                "target_id": link.target_id,
                                "link_type": link.link_type,
                                "confidence": link.confidence
                            }
                            for link in gap.suggested_links
                        ],
                        "resolution_priority": gap.resolution_priority
                    }
                    for gap in gaps
                ],
                "impact_analysis": impact_analysis,
                "recommendations": recommendations,
                "visualization_data": self._prepare_visualization_data(nodes, links, network),
                "metadata": {
                    "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "ai_models_used": ["sentence-transformers", "networkx", "sklearn"],
                    "generation_timestamp": datetime.now().isoformat(),
                    "similarity_threshold": self.similarity_threshold,
                    "confidence_threshold": self.confidence_threshold,
                    "cache_key": cache_key
                }
            }
            
            # Cache results
            self.cache.set(cache_key, results)
            
            # Performance check
            processing_time = (datetime.now() - start_time).total_seconds()
            if processing_time > PERFORMANCE_THRESHOLDS['max_response_time']:
                logger.warning(f"Traceability generation took {processing_time:.2f}s")
            
            logger.info(f"Traceability matrix generated for {organization_id}: {len(nodes)} requirements, {len(links)} links")
            return results
            
        except Exception as e:
            logger.error(f"Traceability matrix generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "organization_id": organization_id,
                "requirements_count": len(requirements),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds()
            }
    
    def _create_requirement_nodes(self, requirements: List[Dict[str, Any]]) -> List[RequirementNode]:
        """Convert requirements to node objects"""
        nodes = []
        
        for req in requirements:
            node = RequirementNode(
                id=req.get('id', f"REQ_{len(nodes) + 1}"),
                text=req.get('text', req.get('description', '')),
                type=req.get('type', 'functional'),
                priority=req.get('priority', 'medium'),
                status=req.get('status', 'draft'),
                metadata=req.get('metadata', {})
            )
            nodes.append(node)
        
        return nodes
    
    async def _generate_embeddings(self, nodes: List[RequirementNode]):
        """Generate semantic embeddings for all requirement nodes"""
        try:
            texts = [node.text for node in nodes]
            embeddings = self.embedding_model.encode(texts, batch_size=32)
            
            for i, node in enumerate(nodes):
                node.embedding = embeddings[i]
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            # Fallback: use TF-IDF vectors
            texts = [node.text for node in nodes]
            if texts:
                tfidf_matrix = self.vectorizer.fit_transform(texts)
                for i, node in enumerate(nodes):
                    node.embedding = tfidf_matrix[i].toarray().flatten()
    
    async def _discover_traceability_links(
        self,
        nodes: List[RequirementNode],
        options: Dict[str, Any]
    ) -> List[TraceabilityLink]:
        """Discover traceability links using semantic analysis"""
        
        links = []
        similarity_threshold = options.get('similarity_threshold', self.similarity_threshold)
        
        # Calculate pairwise similarities
        embeddings = np.vstack([node.embedding for node in nodes])
        similarity_matrix = cosine_similarity(embeddings)
        
        for i, source_node in enumerate(nodes):
            for j, target_node in enumerate(nodes):
                if i == j:
                    continue
                
                similarity = similarity_matrix[i][j]
                
                if similarity >= similarity_threshold:
                    # Determine link type and strength
                    link_type, confidence, rationale = self._determine_link_type(
                        source_node, target_node, similarity
                    )
                    
                    if link_type and confidence >= 0.5:
                        link = TraceabilityLink(
                            source_id=source_node.id,
                            target_id=target_node.id,
                            source_type=source_node.type,
                            target_type=target_node.type,
                            link_type=link_type,
                            confidence=confidence,
                            strength=similarity,
                            rationale=rationale,
                            created_at=datetime.now(),
                            validated=False
                        )
                        links.append(link)
        
        # Sort links by confidence and strength
        links.sort(key=lambda x: (x.confidence, x.strength), reverse=True)
        
        # Apply link filtering and validation
        validated_links = self._validate_and_filter_links(links, nodes)
        
        return validated_links
    
    def _determine_link_type(
        self,
        source_node: RequirementNode,
        target_node: RequirementNode,
        similarity: float
    ) -> Tuple[str, float, str]:
        """Determine the type of traceability link between nodes"""
        
        source_text = source_node.text.lower()
        target_text = target_node.text.lower()
        
        # Pattern-based link type detection
        link_patterns = {
            'implements': {
                'patterns': [
                    (r'implement\w*', r'requirement|specification'),
                    (r'realize\w*', r'requirement|specification'),
                    (r'fulfill\w*', r'requirement|specification')
                ],
                'base_confidence': 0.8
            },
            'derived_from': {
                'patterns': [
                    (r'based\s+on', r'requirement|specification'),
                    (r'derived\s+from', r'requirement|specification'),
                    (r'extends?', r'requirement|specification')
                ],
                'base_confidence': 0.85
            },
            'depends_on': {
                'patterns': [
                    (r'depends?\s+on', r''),
                    (r'requires?', r''),
                    (r'needs?', r'')
                ],
                'base_confidence': 0.75
            },
            'tests': {
                'patterns': [
                    (r'test\w*', r'requirement|function'),
                    (r'verify\w*', r'requirement|function'),
                    (r'validate\w*', r'requirement|function')
                ],
                'base_confidence': 0.9
            },
            'conflicts_with': {
                'patterns': [
                    (r'conflict\w*', r''),
                    (r'contradict\w*', r''),
                    (r'oppose\w*', r'')
                ],
                'base_confidence': 0.7
            }
        }
        
        best_link_type = None
        best_confidence = 0.0
        best_rationale = ""
        
        # Check each link type pattern
        for link_type, config in link_patterns.items():
            for source_pattern, target_pattern in config['patterns']:
                source_match = bool(re.search(source_pattern, source_text))
                target_match = not target_pattern or bool(re.search(target_pattern, target_text))
                
                if source_match and target_match:
                    # Calculate confidence based on similarity and pattern match
                    confidence = (similarity * 0.6) + (config['base_confidence'] * 0.4)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_link_type = link_type
                        best_rationale = f"Pattern match: '{source_pattern}' -> '{target_pattern}'"
        
        # Type-based link inference
        if not best_link_type and similarity > 0.7:
            type_mappings = {
                ('functional', 'test'): ('tested_by', 0.8, "Functional requirement to test case"),
                ('non_functional', 'test'): ('tested_by', 0.8, "Non-functional requirement to test case"),
                ('business', 'functional'): ('derived_from', 0.75, "Functional derived from business requirement"),
                ('functional', 'design'): ('implements', 0.85, "Design implements functional requirement"),
                ('design', 'code'): ('implements', 0.9, "Code implements design specification")
            }
            
            type_key = (source_node.type, target_node.type)
            if type_key in type_mappings:
                link_type, base_conf, rationale = type_mappings[type_key]
                confidence = (similarity * 0.5) + (base_conf * 0.5)
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_link_type = link_type
                    best_rationale = rationale
        
        # Default to 'related_to' for high similarity
        if not best_link_type and similarity > 0.5:
            best_link_type = 'related_to'
            best_confidence = similarity * 0.7
            best_rationale = f"High semantic similarity ({similarity:.3f})"
        
        return best_link_type, best_confidence, best_rationale
    
    def _validate_and_filter_links(
        self,
        links: List[TraceabilityLink],
        nodes: List[RequirementNode]
    ) -> List[TraceabilityLink]:
        """Validate and filter discovered links"""
        
        validated_links = []
        
        # Create node lookup
        node_lookup = {node.id: node for node in nodes}
        
        # Group links by source-target pairs
        pair_links = defaultdict(list)
        for link in links:
            pair_key = (link.source_id, link.target_id)
            pair_links[pair_key].append(link)
        
        # Keep best link for each pair
        for pair_key, pair_link_list in pair_links.items():
            # Sort by confidence and select best
            best_link = max(pair_link_list, key=lambda x: x.confidence)
            
            # Additional validation checks
            if self._is_valid_link(best_link, node_lookup):
                best_link.validated = True
                validated_links.append(best_link)
        
        # Remove circular dependencies and conflicts
        validated_links = self._resolve_link_conflicts(validated_links)
        
        return validated_links
    
    def _is_valid_link(self, link: TraceabilityLink, node_lookup: Dict[str, RequirementNode]) -> bool:
        """Validate if a traceability link is valid"""
        
        # Check if both nodes exist
        if link.source_id not in node_lookup or link.target_id not in node_lookup:
            return False
        
        # Check confidence threshold
        if link.confidence < 0.5:
            return False
        
        # Check for self-links
        if link.source_id == link.target_id:
            return False
        
        # Type-specific validations
        source_node = node_lookup[link.source_id]
        target_node = node_lookup[link.target_id]
        
        # Invalid type combinations
        invalid_combinations = {
            ('test', 'business'): 'tests',  # Tests don't implement business requirements
            ('code', 'business'): 'implements'  # Code doesn't directly implement business
        }
        
        type_pair = (source_node.type, target_node.type)
        if type_pair in invalid_combinations and link.link_type == invalid_combinations[type_pair]:
            return False
        
        return True
    
    def _resolve_link_conflicts(self, links: List[TraceabilityLink]) -> List[TraceabilityLink]:
        """Resolve conflicts between traceability links"""
        
        resolved_links = []
        
        # Group conflicting link types
        conflicting_types = [
            ('implements', 'conflicts_with'),
            ('derived_from', 'conflicts_with'),
            ('depends_on', 'conflicts_with')
        ]
        
        # Create conflict groups
        conflict_groups = defaultdict(list)
        for link in links:
            pair_key = tuple(sorted([link.source_id, link.target_id]))
            conflict_groups[pair_key].append(link)
        
        # Resolve conflicts for each pair
        for pair_key, pair_links in conflict_groups.items():
            if len(pair_links) == 1:
                resolved_links.extend(pair_links)
                continue
            
            # Check for conflicting link types
            link_types = {link.link_type for link in pair_links}
            
            has_conflict = False
            for type1, type2 in conflicting_types:
                if type1 in link_types and type2 in link_types:
                    has_conflict = True
                    break
            
            if has_conflict:
                # Keep the link with highest confidence, exclude conflicts
                non_conflict_links = [
                    link for link in pair_links 
                    if link.link_type != 'conflicts_with'
                ]
                if non_conflict_links:
                    best_link = max(non_conflict_links, key=lambda x: x.confidence)
                    resolved_links.append(best_link)
                else:
                    # If only conflicts, keep the strongest one
                    best_link = max(pair_links, key=lambda x: x.confidence)
                    resolved_links.append(best_link)
            else:
                # No conflicts, keep all links
                resolved_links.extend(pair_links)
        
        return resolved_links
    
    def _build_traceability_network(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink]
    ) -> nx.DiGraph:
        """Build NetworkX graph from traceability links"""
        
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(
                node.id,
                text=node.text,
                type=node.type,
                priority=node.priority,
                status=node.status,
                metadata=node.metadata
            )
        
        # Add edges
        for link in links:
            G.add_edge(
                link.source_id,
                link.target_id,
                link_type=link.link_type,
                confidence=link.confidence,
                strength=link.strength,
                rationale=link.rationale,
                weight=self.link_types.get(link.link_type, {}).get('weight', 0.5)
            )
        
        return G
    
    def _analyze_network_properties(
        self,
        network: nx.DiGraph,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink]
    ) -> Dict[str, Any]:
        """Analyze network properties and metrics"""
        
        analysis = {
            "basic_metrics": {
                "node_count": network.number_of_nodes(),
                "edge_count": network.number_of_edges(),
                "density": nx.density(network),
                "is_connected": nx.is_weakly_connected(network),
                "number_of_components": nx.number_weakly_connected_components(network)
            },
            "centrality_metrics": {},
            "connectivity_analysis": {},
            "path_analysis": {},
            "clustering_metrics": {}
        }
        
        try:
            # Centrality metrics
            degree_centrality = nx.degree_centrality(network)
            betweenness_centrality = nx.betweenness_centrality(network)
            closeness_centrality = nx.closeness_centrality(network)
            
            # Find most central nodes
            top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analysis["centrality_metrics"] = {
                "degree_centrality": degree_centrality,
                "betweenness_centrality": betweenness_centrality,
                "closeness_centrality": closeness_centrality,
                "most_connected_requirements": [{"id": node_id, "centrality": cent} for node_id, cent in top_degree],
                "most_critical_requirements": [{"id": node_id, "betweenness": bet} for node_id, bet in top_betweenness]
            }
            
            # Connectivity analysis
            isolated_nodes = list(nx.isolates(network))
            in_degree = dict(network.in_degree())
            out_degree = dict(network.out_degree())
            
            # Find requirements with no incoming/outgoing links
            orphaned_requirements = [node_id for node_id, degree in in_degree.items() if degree == 0]
            dead_end_requirements = [node_id for node_id, degree in out_degree.items() if degree == 0]
            
            analysis["connectivity_analysis"] = {
                "isolated_nodes": isolated_nodes,
                "orphaned_requirements": orphaned_requirements,
                "dead_end_requirements": dead_end_requirements,
                "average_in_degree": sum(in_degree.values()) / len(in_degree) if in_degree else 0,
                "average_out_degree": sum(out_degree.values()) / len(out_degree) if out_degree else 0
            }
            
            # Path analysis
            if nx.is_weakly_connected(network):
                avg_shortest_path = nx.average_shortest_path_length(network.to_undirected())
                diameter = nx.diameter(network.to_undirected())
                
                analysis["path_analysis"] = {
                    "average_shortest_path_length": avg_shortest_path,
                    "diameter": diameter,
                    "radius": nx.radius(network.to_undirected())
                }
            
            # Clustering metrics
            clustering_coefficient = nx.average_clustering(network.to_undirected())
            
            analysis["clustering_metrics"] = {
                "average_clustering_coefficient": clustering_coefficient,
                "transitivity": nx.transitivity(network.to_undirected())
            }
            
        except Exception as e:
            logger.error(f"Network analysis failed: {str(e)}")
            analysis["error"] = str(e)
        
        return analysis
    
    def _identify_traceability_gaps(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink],
        network: nx.DiGraph
    ) -> List[TraceabilityGap]:
        """Identify gaps in traceability coverage"""
        
        gaps = []
        
        # Create link lookup for efficiency
        link_pairs = {(link.source_id, link.target_id) for link in links}
        
        # Gap 1: Isolated requirements
        isolated_nodes = list(nx.isolates(network))
        if isolated_nodes:
            gap = TraceabilityGap(
                gap_id="GAP_ISOLATED_001",
                gap_type="isolated_requirements",
                description=f"Found {len(isolated_nodes)} requirements with no traceability links",
                severity="high",
                affected_requirements=isolated_nodes,
                suggested_links=[],
                resolution_priority=1
            )
            gaps.append(gap)
        
        # Gap 2: Missing forward traceability
        forward_gaps = []
        for node in nodes:
            if node.type in ['business', 'functional']:
                has_forward_link = any(
                    link.source_id == node.id and link.target_type in ['design', 'test', 'implementation']
                    for link in links
                )
                if not has_forward_link:
                    forward_gaps.append(node.id)
        
        if forward_gaps:
            gap = TraceabilityGap(
                gap_id="GAP_FORWARD_001",
                gap_type="missing_forward_traceability",
                description=f"Found {len(forward_gaps)} requirements without forward traceability",
                severity="medium",
                affected_requirements=forward_gaps,
                suggested_links=self._suggest_forward_links(forward_gaps, nodes, links),
                resolution_priority=2
            )
            gaps.append(gap)
        
        # Gap 3: Missing backward traceability
        backward_gaps = []
        for node in nodes:
            if node.type in ['design', 'test', 'implementation']:
                has_backward_link = any(
                    link.target_id == node.id and link.source_type in ['business', 'functional']
                    for link in links
                )
                if not has_backward_link:
                    backward_gaps.append(node.id)
        
        if backward_gaps:
            gap = TraceabilityGap(
                gap_id="GAP_BACKWARD_001",
                gap_type="missing_backward_traceability",
                description=f"Found {len(backward_gaps)} items without backward traceability",
                severity="medium",
                affected_requirements=backward_gaps,
                suggested_links=self._suggest_backward_links(backward_gaps, nodes, links),
                resolution_priority=3
            )
            gaps.append(gap)
        
        # Gap 4: Circular dependencies
        try:
            cycles = list(nx.simple_cycles(network))
            if cycles:
                affected_reqs = list(set(req for cycle in cycles for req in cycle))
                gap = TraceabilityGap(
                    gap_id="GAP_CIRCULAR_001",
                    gap_type="circular_dependencies",
                    description=f"Found {len(cycles)} circular dependency cycles",
                    severity="high",
                    affected_requirements=affected_reqs,
                    suggested_links=[],
                    resolution_priority=1
                )
                gaps.append(gap)
        except Exception as e:
            logger.warning(f"Cycle detection failed: {str(e)}")
        
        # Sort gaps by priority
        gaps.sort(key=lambda x: x.resolution_priority)
        
        return gaps
    
    def _suggest_forward_links(
        self,
        gap_requirements: List[str],
        nodes: List[RequirementNode],
        existing_links: List[TraceabilityLink]
    ) -> List[TraceabilityLink]:
        """Suggest forward traceability links for gap requirements"""
        
        suggestions = []
        node_lookup = {node.id: node for node in nodes}
        
        for req_id in gap_requirements:
            if req_id not in node_lookup:
                continue
                
            source_node = node_lookup[req_id]
            
            # Find potential targets (design, test, implementation items)
            potential_targets = [
                node for node in nodes 
                if node.type in ['design', 'test', 'implementation'] and 
                   node.id != req_id
            ]
            
            if not potential_targets:
                continue
            
            # Calculate similarities and suggest best matches
            source_embedding = source_node.embedding
            if source_embedding is not None:
                for target_node in potential_targets:
                    if target_node.embedding is not None:
                        similarity = cosine_similarity(
                            source_embedding.reshape(1, -1),
                            target_node.embedding.reshape(1, -1)
                        )[0][0]
                        
                        if similarity > 0.4:  # Lower threshold for suggestions
                            link = TraceabilityLink(
                                source_id=source_node.id,
                                target_id=target_node.id,
                                source_type=source_node.type,
                                target_type=target_node.type,
                                link_type='implements' if target_node.type == 'design' else 'tested_by',
                                confidence=similarity * 0.8,  # Lower confidence for suggestions
                                strength=similarity,
                                rationale=f"Suggested forward link based on similarity ({similarity:.3f})",
                                created_at=datetime.now(),
                                validated=False
                            )
                            suggestions.append(link)
        
        # Sort by confidence and limit suggestions
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def _suggest_backward_links(
        self,
        gap_requirements: List[str],
        nodes: List[RequirementNode],
        existing_links: List[TraceabilityLink]
    ) -> List[TraceabilityLink]:
        """Suggest backward traceability links for gap requirements"""
        
        suggestions = []
        node_lookup = {node.id: node for node in nodes}
        
        for req_id in gap_requirements:
            if req_id not in node_lookup:
                continue
                
            target_node = node_lookup[req_id]
            
            # Find potential sources (business, functional requirements)
            potential_sources = [
                node for node in nodes 
                if node.type in ['business', 'functional'] and 
                   node.id != req_id
            ]
            
            if not potential_sources:
                continue
            
            # Calculate similarities and suggest best matches
            target_embedding = target_node.embedding
            if target_embedding is not None:
                for source_node in potential_sources:
                    if source_node.embedding is not None:
                        similarity = cosine_similarity(
                            source_node.embedding.reshape(1, -1),
                            target_embedding.reshape(1, -1)
                        )[0][0]
                        
                        if similarity > 0.4:  # Lower threshold for suggestions
                            link = TraceabilityLink(
                                source_id=source_node.id,
                                target_id=target_node.id,
                                source_type=source_node.type,
                                target_type=target_node.type,
                                link_type='derived_from',
                                confidence=similarity * 0.8,
                                strength=similarity,
                                rationale=f"Suggested backward link based on similarity ({similarity:.3f})",
                                created_at=datetime.now(),
                                validated=False
                            )
                            suggestions.append(link)
        
        # Sort by confidence and limit suggestions
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:10]
    
    def _generate_matrix_data(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink]
    ) -> Dict[str, Any]:
        """Generate traceability matrix data structure"""
        
        # Group nodes by type
        node_types = {}
        for node in nodes:
            if node.type not in node_types:
                node_types[node.type] = []
            node_types[node.type].append(node)
        
        # Create matrix structure
        matrix = {
            "row_types": list(node_types.keys()),
            "column_types": list(node_types.keys()),
            "matrix_cells": {},
            "summary": {
                "total_cells": 0,
                "linked_cells": 0,
                "coverage_by_type": {}
            }
        }
        
        # Build matrix cells
        for row_type in node_types:
            for col_type in node_types:
                cell_key = f"{row_type}_to_{col_type}"
                matrix["matrix_cells"][cell_key] = {
                    "source_type": row_type,
                    "target_type": col_type,
                    "links": [],
                    "link_count": 0,
                    "coverage_percentage": 0.0
                }
        
        # Populate matrix with links
        for link in links:
            source_node = next((n for n in nodes if n.id == link.source_id), None)
            target_node = next((n for n in nodes if n.id == link.target_id), None)
            
            if source_node and target_node:
                cell_key = f"{source_node.type}_to_{target_node.type}"
                if cell_key in matrix["matrix_cells"]:
                    matrix["matrix_cells"][cell_key]["links"].append({
                        "source_id": link.source_id,
                        "target_id": link.target_id,
                        "link_type": link.link_type,
                        "confidence": link.confidence
                    })
                    matrix["matrix_cells"][cell_key]["link_count"] += 1
        
        # Calculate coverage percentages
        for cell_key, cell_data in matrix["matrix_cells"].items():
            source_type = cell_data["source_type"]
            target_type = cell_data["target_type"]
            
            source_count = len(node_types.get(source_type, []))
            target_count = len(node_types.get(target_type, []))
            
            if source_count > 0 and target_count > 0:
                max_possible_links = source_count * target_count
                coverage = (cell_data["link_count"] / max_possible_links) * 100
                cell_data["coverage_percentage"] = round(coverage, 2)
            
            matrix["summary"]["total_cells"] += 1
            if cell_data["link_count"] > 0:
                matrix["summary"]["linked_cells"] += 1
        
        # Calculate coverage by type
        for req_type, type_nodes in node_types.items():
            linked_nodes = set()
            for link in links:
                if link.source_id in [n.id for n in type_nodes]:
                    linked_nodes.add(link.source_id)
                if link.target_id in [n.id for n in type_nodes]:
                    linked_nodes.add(link.target_id)
            
            coverage = (len(linked_nodes) / len(type_nodes)) * 100 if type_nodes else 0
            matrix["summary"]["coverage_by_type"][req_type] = round(coverage, 2)
        
        return matrix
    
    def _calculate_change_impact(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink],
        network: nx.DiGraph
    ) -> Dict[str, Any]:
        """Calculate change impact analysis for each requirement"""
        
        impact_analysis = {
            "high_impact_requirements": [],
            "change_propagation_paths": {},
            "dependency_clusters": [],
            "risk_assessment": {}
        }
        
        try:
            # Calculate impact scores based on network centrality
            degree_centrality = nx.degree_centrality(network)
            betweenness_centrality = nx.betweenness_centrality(network)
            
            # Identify high-impact requirements
            for node_id, degree in degree_centrality.items():
                betweenness = betweenness_centrality.get(node_id, 0)
                impact_score = (degree * 0.6) + (betweenness * 0.4)
                
                if impact_score > 0.1:  # Threshold for high impact
                    node_data = network.nodes.get(node_id, {})
                    impact_analysis["high_impact_requirements"].append({
                        "requirement_id": node_id,
                        "impact_score": round(impact_score, 3),
                        "degree_centrality": round(degree, 3),
                        "betweenness_centrality": round(betweenness, 3),
                        "type": node_data.get('type', 'unknown'),
                        "priority": node_data.get('priority', 'unknown')
                    })
            
            # Sort by impact score
            impact_analysis["high_impact_requirements"].sort(
                key=lambda x: x["impact_score"], 
                reverse=True
            )
            
            # Calculate change propagation paths
            for node in nodes[:10]:  # Limit to first 10 for performance
                try:
                    # Forward propagation (what would be affected)
                    descendants = list(nx.descendants(network, node.id))
                    # Backward propagation (what affects this)
                    ancestors = list(nx.ancestors(network, node.id))
                    
                    impact_analysis["change_propagation_paths"][node.id] = {
                        "forward_impact": descendants,
                        "backward_dependencies": ancestors,
                        "total_impact_scope": len(set(descendants + ancestors))
                    }
                except Exception as e:
                    logger.warning(f"Path calculation failed for {node.id}: {str(e)}")
            
            # Identify dependency clusters using community detection
            if network.number_of_nodes() > 0:
                undirected_graph = network.to_undirected()
                try:
                    import networkx.algorithms.community as nx_comm
                    communities = nx_comm.greedy_modularity_communities(undirected_graph)
                    
                    for i, community in enumerate(communities):
                        if len(community) > 2:  # Only include meaningful clusters
                            impact_analysis["dependency_clusters"].append({
                                "cluster_id": f"CLUSTER_{i+1}",
                                "requirements": list(community),
                                "size": len(community),
                                "internal_links": len([
                                    link for link in links
                                    if link.source_id in community and link.target_id in community
                                ])
                            })
                except ImportError:
                    logger.warning("Community detection not available")
                except Exception as e:
                    logger.warning(f"Community detection failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Impact analysis calculation failed: {str(e)}")
            impact_analysis["error"] = str(e)
        
        return impact_analysis
    
    def _calculate_coverage_percentage(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink]
    ) -> float:
        """Calculate overall traceability coverage percentage"""
        
        if not nodes:
            return 0.0
        
        # Count nodes with at least one link
        linked_nodes = set()
        for link in links:
            linked_nodes.add(link.source_id)
            linked_nodes.add(link.target_id)
        
        coverage = (len(linked_nodes) / len(nodes)) * 100
        return round(coverage, 2)
    
    def _generate_traceability_recommendations(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink],
        gaps: List[TraceabilityGap],
        network_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate recommendations for improving traceability"""
        
        recommendations = {
            "immediate_actions": [],
            "coverage_improvements": [],
            "quality_enhancements": [],
            "process_improvements": [],
            "tool_suggestions": []
        }
        
        # Immediate actions based on gaps
        high_priority_gaps = [gap for gap in gaps if gap.severity in ['critical', 'high']]
        if high_priority_gaps:
            recommendations["immediate_actions"].append(
                f"Address {len(high_priority_gaps)} high-priority traceability gaps"
            )
        
        isolated_count = len(network_analysis.get("connectivity_analysis", {}).get("isolated_nodes", []))
        if isolated_count > 0:
            recommendations["immediate_actions"].append(
                f"Connect {isolated_count} isolated requirements to traceability network"
            )
        
        # Coverage improvements
        coverage_percentage = self._calculate_coverage_percentage(nodes, links)
        if coverage_percentage < 80:
            recommendations["coverage_improvements"].append(
                f"Improve overall coverage from {coverage_percentage}% to at least 80%"
            )
        
        orphaned_count = len(network_analysis.get("connectivity_analysis", {}).get("orphaned_requirements", []))
        if orphaned_count > 0:
            recommendations["coverage_improvements"].append(
                f"Establish forward traceability for {orphaned_count} orphaned requirements"
            )
        
        # Quality enhancements
        low_confidence_links = [link for link in links if link.confidence < 0.7]
        if len(low_confidence_links) > len(links) * 0.2:  # More than 20%
            recommendations["quality_enhancements"].append(
                f"Review and validate {len(low_confidence_links)} low-confidence traceability links"
            )
        
        unvalidated_links = [link for link in links if not link.validated]
        if unvalidated_links:
            recommendations["quality_enhancements"].append(
                f"Validate {len(unvalidated_links)} automatically generated traceability links"
            )
        
        # Process improvements
        if len(nodes) > 100:
            recommendations["process_improvements"].append(
                "Implement automated traceability maintenance for large requirement sets"
            )
        
        density = network_analysis.get("basic_metrics", {}).get("density", 0)
        if density < 0.1:
            recommendations["process_improvements"].append(
                "Establish clearer traceability policies - network density is low"
            )
        elif density > 0.5:
            recommendations["process_improvements"].append(
                "Review over-linking - network density may be too high"
            )
        
        # Tool suggestions
        if len(nodes) > 50:
            recommendations["tool_suggestions"].append(
                "Consider implementing automated traceability tools for better maintenance"
            )
        
        if gaps:
            recommendations["tool_suggestions"].append(
                "Use AI-powered gap analysis for continuous traceability monitoring"
            )
        
        return recommendations
    
    def _prepare_visualization_data(
        self,
        nodes: List[RequirementNode],
        links: List[TraceabilityLink],
        network: nx.DiGraph
    ) -> Dict[str, Any]:
        """Prepare data for traceability visualization"""
        
        # Calculate layout positions
        try:
            if network.number_of_nodes() > 0:
                pos = nx.spring_layout(network, k=1, iterations=50)
            else:
                pos = {}
        except:
            pos = {}
        
        # Prepare node data for visualization
        vis_nodes = []
        for node in nodes:
            node_pos = pos.get(node.id, (0, 0))
            vis_nodes.append({
                "id": node.id,
                "text": node.text[:100] + "..." if len(node.text) > 100 else node.text,
                "type": node.type,
                "priority": node.priority,
                "status": node.status,
                "x": float(node_pos[0]),
                "y": float(node_pos[1]),
                "degree": network.degree(node.id) if node.id in network else 0
            })
        
        # Prepare edge data for visualization
        vis_edges = []
        for link in links:
            vis_edges.append({
                "source": link.source_id,
                "target": link.target_id,
                "link_type": link.link_type,
                "confidence": link.confidence,
                "strength": link.strength,
                "validated": link.validated
            })
        
        return {
            "nodes": vis_nodes,
            "edges": vis_edges,
            "layout": "spring",
            "node_types": list(set(node.type for node in nodes)),
            "link_types": list(self.link_types.keys()),
            "statistics": {
                "total_nodes": len(vis_nodes),
                "total_edges": len(vis_edges),
                "avg_degree": sum(node["degree"] for node in vis_nodes) / len(vis_nodes) if vis_nodes else 0
            }
        }
    
    def _generate_requirements_hash(self, requirements: List[Dict[str, Any]]) -> str:
        """Generate hash for requirements list for caching"""
        req_texts = [req.get('text', req.get('description', '')) for req in requirements]
        content = '|'.join(sorted(req_texts))
        return hashlib.md5(content.encode()).hexdigest()[:16]

# Initialize traceability engine
traceability_engine = IntelligentTraceabilityMatrix()

async def traceability_matrix_tool(organization_id: str, message: str) -> Dict[str, Any]:
    """
    Intelligent Traceability Matrix Generator Tool
    
    Purpose: Automated traceability matrix generation with semantic link analysis
    Expected Benefits:
    - 80% reduction in traceability matrix generation time
    - Automatic semantic similarity-based linking
    - Network analysis for traceability visualization
    - Change impact analysis with dependency mapping
    - Automated gap identification and resolution
    
    Args:
        organization_id (str): Organization identifier for data isolation
        message (str): JSON string containing requirements and generation options
        
    Returns:
        Dict[str, Any]: Comprehensive traceability matrix with analysis and visualizations
        
    Matrix Features:
        - Semantic similarity-based link discovery
        - Multi-type requirement support (business, functional, design, test, etc.)
        - Network analysis with centrality metrics
        - Gap identification and resolution suggestions
        - Change impact analysis and dependency mapping
        - Interactive visualization data
        - Coverage metrics and quality assessment
    """
    
    try:
        logger.info(f"Starting traceability matrix generation for org {organization_id}")
        
        # Parse message to extract requirements and options
        try:
            if message.startswith('{'):
                data = json.loads(message)
                requirements = data.get('requirements', [])
                options = data.get('options', {})
            else:
                # Fallback: treat message as simple text request
                return {
                    "success": False,
                    "error": "Invalid input format. Expected JSON with 'requirements' array",
                    "example": {
                        "requirements": [
                            {
                                "id": "BR-001", 
                                "text": "The system shall support user authentication",
                                "type": "business",
                                "priority": "high"
                            },
                            {
                                "id": "FR-001",
                                "text": "The system shall authenticate users using username and password", 
                                "type": "functional",
                                "priority": "high"
                            }
                        ],
                        "options": {
                            "similarity_threshold": 0.3,
                            "include_visualizations": True,
                            "force_regenerate": False
                        }
                    }
                }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing failed: {str(e)}",
                "message": message[:100] + "..." if len(message) > 100 else message
            }
        
        if not requirements:
            return {
                "success": False,
                "error": "No requirements provided for traceability matrix generation",
                "requirements_count": 0
            }
        
        # Generate traceability matrix
        result = await traceability_engine.generate_traceability_matrix(
            organization_id, 
            requirements, 
            options
        )
        
        # Add request context
        result["request_context"] = {
            "original_message_length": len(message),
            "requirements_processed": len(requirements),
            "options_used": options,
            "organization_id": organization_id,
            "generation_timestamp": datetime.now().isoformat(),
            "ai_models_available": traceability_engine.enabled
        }
        
        logger.info(f"Traceability matrix generated for org {organization_id}: {len(requirements)} requirements processed")
        return result
        
    except Exception as e:
        logger.error(f"Traceability matrix tool failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message[:100] + "..." if len(message) > 100 else message,
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }

# Synchronous wrapper for FastMCP compatibility
def traceability_matrix_tool_sync(organization_id: str, message: str) -> Dict[str, Any]:
    """Synchronous wrapper for traceability matrix generation"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(traceability_matrix_tool(organization_id, message))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Traceability matrix sync wrapper failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": message[:100] + "..." if len(message) > 100 else message,
            "organization_id": organization_id
        }