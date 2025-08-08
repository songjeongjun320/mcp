"""
ATOMS.TECH Intelligence Tools Configuration
Phase 3 - Custom Requirements Intelligence

Configuration settings for AI/ML-powered intelligence tools.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
CACHE_DIR = BASE_DIR / "cache"
AI_MODELS_CACHE = CACHE_DIR / "ai_models"
EMBEDDINGS_CACHE = CACHE_DIR / "embeddings"
LOGS_DIR = BASE_DIR / "logs" / "intelligence"

# Ensure directories exist
AI_MODELS_CACHE.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_CACHE.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Phase 3 Intelligence Configuration
INTELLIGENCE_CONFIG = {
    'enabled': True,
    'ai_model_cache_size': 1000,
    'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
    'realtime_monitoring_interval': 30,
    'max_concurrent_analysis': 5,
    'max_embedding_batch_size': 100,
    'cache_ttl': 3600,
    'compliance_standards': ['GDPR', 'ISO27001', 'IEEE830', 'NIST'],
    'prediction_accuracy_threshold': 0.85,
    'recommendation_confidence_threshold': 0.90
}

# AI Model Configuration
AI_MODELS = {
    'requirements_validator': {
        'model_type': 'classification',
        'cache_enabled': True,
        'max_cache_size': 500
    },
    'traceability_analyzer': {
        'model_type': 'embedding',
        'cache_enabled': True,
        'max_cache_size': 1000
    },
    'impact_predictor': {
        'model_type': 'regression',
        'cache_enabled': True,
        'max_cache_size': 300
    },
    'compliance_monitor': {
        'model_type': 'rule_based',
        'cache_enabled': True,
        'max_cache_size': 200
    },
    'recommendation_engine': {
        'model_type': 'collaborative_filtering',
        'cache_enabled': True,
        'max_cache_size': 800
    }
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'max_response_time': 3.0,  # seconds
    'min_accuracy': 0.90,
    'max_memory_usage': 512,   # MB
    'max_cpu_usage': 80        # percentage
}

# Logging Configuration for Intelligence Tools
def setup_intelligence_logging(tool_name: str) -> logging.Logger:
    """Setup logging for intelligence tools"""
    logger = logging.getLogger(f'atoms.intelligence.{tool_name}')
    logger.setLevel(logging.INFO)
    
    # File handler
    log_file = LOGS_DIR / f"{tool_name}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler  
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Cache Management
class IntelligenceCache:
    """Cache management for intelligence tools"""
    
    def __init__(self, cache_type: str, max_size: int = 1000):
        self.cache_type = cache_type
        self.max_size = max_size
        self.cache = {}
        
    def get(self, key: str) -> Any:
        """Get cached value"""
        return self.cache.get(key)
        
    def set(self, key: str, value: Any) -> None:
        """Set cached value with size limit"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

# Global cache instances
GLOBAL_CACHES = {
    'embeddings': IntelligenceCache('embeddings', 1000),
    'predictions': IntelligenceCache('predictions', 500),
    'compliance': IntelligenceCache('compliance', 300),
    'recommendations': IntelligenceCache('recommendations', 800)
}

def get_cache(cache_type: str) -> IntelligenceCache:
    """Get cache instance by type"""
    return GLOBAL_CACHES.get(cache_type, IntelligenceCache(cache_type))