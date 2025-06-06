from typing import Any, Dict, Optional
import hashlib
import json
import logging
from datetime import datetime, timedelta
import redis
from .base import ModelResponse

logger = logging.getLogger(__name__)

class ModelCache:
    """Cache system for model responses."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,  # 1 hour
        max_cache_size: int = 1000
    ):
        self.redis = redis.Redis.from_url(redis_url)
        self.default_ttl = default_ttl
        self.max_cache_size = max_cache_size
    
    def _generate_cache_key(
        self,
        model_name: str,
        prompt: str,
        **kwargs
    ) -> str:
        """Generate a unique cache key for the request."""
        # Sort kwargs to ensure consistent key generation
        sorted_kwargs = json.dumps(kwargs, sort_keys=True)
        key_string = f"{model_name}:{prompt}:{sorted_kwargs}"
        return f"model_cache:{hashlib.sha256(key_string.encode()).hexdigest()}"
    
    async def get_cached_response(
        self,
        model_name: str,
        prompt: str,
        **kwargs
    ) -> Optional[ModelResponse]:
        """Get a cached response if available."""
        try:
            cache_key = self._generate_cache_key(model_name, prompt, **kwargs)
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return ModelResponse(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached response: {str(e)}")
            return None
    
    async def cache_response(
        self,
        model_name: str,
        prompt: str,
        response: ModelResponse,
        ttl: Optional[int] = None,
        **kwargs
    ) -> None:
        """Cache a model response."""
        try:
            cache_key = self._generate_cache_key(model_name, prompt, **kwargs)
            
            # Add cache metadata
            response_dict = response.dict()
            response_dict["cached_at"] = datetime.now().isoformat()
            response_dict["cache_ttl"] = ttl or self.default_ttl
            
            # Store in Redis
            self.redis.setex(
                cache_key,
                ttl or self.default_ttl,
                json.dumps(response_dict)
            )
            
            # Update cache statistics
            self._update_cache_stats(model_name)
            
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")
    
    def _update_cache_stats(self, model_name: str) -> None:
        """Update cache statistics."""
        try:
            stats_key = f"model_cache_stats:{model_name}"
            pipe = self.redis.pipeline()
            
            # Increment total cached responses
            pipe.hincrby(stats_key, "total_cached", 1)
            
            # Update last cache time
            pipe.hset(stats_key, "last_cached", datetime.now().isoformat())
            
            # Execute pipeline
            pipe.execute()
            
        except Exception as e:
            logger.error(f"Error updating cache stats: {str(e)}")
    
    async def get_cache_stats(self, model_name: str) -> Dict[str, Any]:
        """Get cache statistics for a model."""
        try:
            stats_key = f"model_cache_stats:{model_name}"
            stats = self.redis.hgetall(stats_key)
            
            return {
                "total_cached": int(stats.get(b"total_cached", 0)),
                "last_cached": stats.get(b"last_cached", "").decode(),
                "cache_hits": int(stats.get(b"cache_hits", 0)),
                "cache_misses": int(stats.get(b"cache_misses", 0))
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    async def clear_cache(self, model_name: Optional[str] = None) -> None:
        """Clear the cache for a specific model or all models."""
        try:
            if model_name:
                pattern = f"model_cache:{model_name}:*"
            else:
                pattern = "model_cache:*"
            
            # Delete matching keys
            for key in self.redis.scan_iter(match=pattern):
                self.redis.delete(key)
            
            logger.info(f"Cleared cache for {model_name or 'all models'}")
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
    
    async def get_cache_size(self) -> int:
        """Get the current cache size."""
        try:
            return len(list(self.redis.scan_iter(match="model_cache:*")))
        except Exception as e:
            logger.error(f"Error getting cache size: {str(e)}")
            return 0 