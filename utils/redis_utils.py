class RedisUtils:
    def generate_active_url_redis_key(short_url):
        return f"urls:active:{short_url}"


    def generate_expired_url_redis_key(short_url):
        return f"urls:expired:{short_url}"
