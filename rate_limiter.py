# src/rate_limiter.py
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier (IP, user_id, etc.)
        
        Returns:
            True if allowed, False if rate limit exceeded
        """
        now = datetime.now()
        
        # Clean up old requests
        self.requests[client_id] = [
            timestamp for timestamp in self.requests[client_id]
            if now - timestamp < self.window
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True
    
    def check(self, request: Request) -> None:
        """
        Check rate limit and raise exception if exceeded.
        
        Args:
            request: FastAPI request object
        
        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        client_ip = request.client.host
        
        if not self.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window.seconds} seconds."
            )
