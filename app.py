from flask import Flask, request, jsonify
from limiter import RateLimiter
import redis

app = Flask(__name__)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

rate_limiter = RateLimiter(
    rate=1,                
    max_tokens=5,          
    refill_interval=1,
    redis_client=redis_client,
    hash_key=False
)

@app.before_request
def limit_requests():
    ip = request.remote_addr
    if not rate_limiter.is_request_allowed(ip):
        return jsonify({"error": "Too many requests"}), 429

@app.route('/')
def home():
    return jsonify({"message": "Hello, Flask with Rate Limiter!"})

if __name__ == "__main__":
    app.run(debug=True)
