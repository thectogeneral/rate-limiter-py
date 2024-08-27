import time
import math
import redis
from flask import request, jsonify

class RateLimiter:
    def __init__(self, rate, max_tokens, refill_interval, redis_client, hash_key=False):
        self.rate = rate
        self.max_tokens = max_tokens
        self.refill_interval = refill_interval
        self.redis_client = redis_client
        self.hash_key = hash_key
        self.key_prefix = "ls_prefix:"
        self.last_refill_prefix = "_lastRefillTime"

    def encode_key(self, value):
        return value.encode('utf-8').hex() if self.hash_key else value

    def is_request_allowed(self, key):
        redis_key = self.key_prefix + self.encode_key(key)
        last_refill_time_key = redis_key + self.last_refill_prefix

        current_tokens = self.redis_client.get(redis_key)
        if current_tokens is None:
            current_tokens = self.max_tokens
        else:
            current_tokens = int(current_tokens)

        last_refill_time = self.redis_client.get(last_refill_time_key)
        if last_refill_time is None:
            last_refill_time = time.time()
        else:
            last_refill_time = float(last_refill_time)

        current_tokens = self.refill(current_tokens, last_refill_time)

        if current_tokens >= self.rate:
            current_tokens -= self.rate
            self.redis_client.set(redis_key, current_tokens)
            self.redis_client.set(last_refill_time_key, time.time())
            return True

        self.redis_client.set(last_refill_time_key, time.time())
        return False

    def refill(self, current_tokens, last_refill_time):
        now = time.time()
        elapsed = now - last_refill_time
        tokens_to_add = elapsed / self.refill_interval
        return min(current_tokens + tokens_to_add, self.max_tokens)
