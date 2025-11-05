import redis
import os
import json
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager for user context and predictions"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD', None),
                decode_responses=True
            )
            self.ttl = int(os.getenv('REDIS_CACHE_TTL', 3600))
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def get(self, key):
        """Get value from cache"""
        try:
            if not self.redis_client:
                return None
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get failed: {str(e)}")
            return None
    
    def set(self, key, value, ttl=None):
        """Set value in cache"""
        try:
            if not self.redis_client:
                return False
            ttl = ttl or self.ttl
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set failed: {str(e)}")
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        try:
            if not self.redis_client:
                return False
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete failed: {str(e)}")
            return False
    
    def get_user_context(self, user_id):
        """Get user context from cache"""
        return self.get(f"user_context:{user_id}")
    
    def set_user_context(self, user_id, context):
        """Set user context in cache"""
        return self.set(f"user_context:{user_id}", context)
    
    def get_prediction(self, user_id):
        """Get prediction from cache"""
        return self.get(f"prediction:{user_id}")
    
    def set_prediction(self, user_id, prediction):
        """Set prediction in cache"""
        return self.set(f"prediction:{user_id}", prediction, ttl=86400)  # 24 hours

# Global instance
redis_cache = RedisCache()
