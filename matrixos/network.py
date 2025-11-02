"""
MatrixOS Network Module
Async HTTP client using urllib + async_tasks for non-blocking network I/O

Zero dependencies - uses Python standard library only.
"""

import urllib.request
import urllib.parse
import urllib.error
import json
from typing import Optional, Dict, Any, Callable
from matrixos.async_tasks import schedule_task, TaskResult


class NetworkError(Exception):
    """Base exception for network errors."""
    pass


class TimeoutError(NetworkError):
    """Request timed out."""
    pass


class ConnectionError(NetworkError):
    """Failed to connect."""
    pass


class HTTPError(NetworkError):
    """HTTP error response."""
    def __init__(self, code, message):
        super().__init__(f"HTTP {code}: {message}")
        self.code = code


class NetworkClient:
    """
    Async HTTP client for MatrixOS apps.
    
    All requests are non-blocking and run in background threads.
    Callbacks run on the main thread, safe for UI updates.
    
    Example:
        def on_weather(result):
            if result.success:
                data = result.value
                self.temperature = data['temp']
                self.dirty = True
            else:
                print(f"Error: {result.error}")
        
        network = NetworkClient(timeout=5.0)
        network.get("https://api.weather.com/current", callback=on_weather)
    """
    
    def __init__(self, timeout=10.0, user_agent="MatrixOS/1.0"):
        """
        Initialize network client.
        
        Args:
            timeout: Request timeout in seconds (default 10.0)
            user_agent: User-Agent header
        """
        self.timeout = timeout
        self.user_agent = user_agent
        self.default_headers = {
            'User-Agent': user_agent,
        }
    
    def get(self, url: str, 
            callback: Optional[Callable[[TaskResult], None]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None) -> None:
        """
        Perform async GET request.
        
        Args:
            url: URL to request
            callback: Called with TaskResult when complete (on main thread)
            headers: Additional HTTP headers
            timeout: Override default timeout
        """
        def fetch():
            return self._do_request('GET', url, headers=headers, timeout=timeout)
        
        schedule_task(fetch, callback)
    
    def get_json(self, url: str,
                 callback: Optional[Callable[[TaskResult], None]] = None,
                 headers: Optional[Dict[str, str]] = None,
                 timeout: Optional[float] = None) -> None:
        """
        Perform async GET request and parse JSON response.
        
        Args:
            url: URL to request
            callback: Called with TaskResult containing parsed JSON (on main thread)
            headers: Additional HTTP headers
            timeout: Override default timeout
        """
        def fetch():
            response = self._do_request('GET', url, headers=headers, timeout=timeout)
            return json.loads(response)
        
        schedule_task(fetch, callback)
    
    def post(self, url: str,
             data: Optional[Dict[str, Any]] = None,
             callback: Optional[Callable[[TaskResult], None]] = None,
             headers: Optional[Dict[str, str]] = None,
             timeout: Optional[float] = None) -> None:
        """
        Perform async POST request.
        
        Args:
            url: URL to request
            data: Dictionary to send as JSON body
            callback: Called with TaskResult when complete (on main thread)
            headers: Additional HTTP headers
            timeout: Override default timeout
        """
        def fetch():
            return self._do_request('POST', url, data=data, headers=headers, timeout=timeout)
        
        schedule_task(fetch, callback)
    
    def post_json(self, url: str,
                  data: Optional[Dict[str, Any]] = None,
                  callback: Optional[Callable[[TaskResult], None]] = None,
                  headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[float] = None) -> None:
        """
        Perform async POST request and parse JSON response.
        
        Args:
            url: URL to request
            data: Dictionary to send as JSON body
            callback: Called with TaskResult containing parsed JSON (on main thread)
            headers: Additional HTTP headers
            timeout: Override default timeout
        """
        def fetch():
            response = self._do_request('POST', url, data=data, headers=headers, timeout=timeout)
            return json.loads(response)
        
        schedule_task(fetch, callback)
    
    def _do_request(self, method: str, url: str,
                   data: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   timeout: Optional[float] = None) -> str:
        """
        Perform synchronous HTTP request (runs in background thread).
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            data: Dictionary to send as JSON body (for POST)
            headers: Additional HTTP headers
            timeout: Request timeout
            
        Returns:
            Response body as string
            
        Raises:
            NetworkError: On network or HTTP errors
        """
        # Merge headers
        req_headers = dict(self.default_headers)
        if headers:
            req_headers.update(headers)
        
        # Prepare request
        req_data = None
        if data is not None:
            req_data = json.dumps(data).encode('utf-8')
            req_headers['Content-Type'] = 'application/json'
        
        request = urllib.request.Request(
            url,
            data=req_data,
            headers=req_headers,
            method=method
        )
        
        # Perform request
        timeout_val = timeout if timeout is not None else self.timeout
        
        try:
            with urllib.request.urlopen(request, timeout=timeout_val) as response:
                return response.read().decode('utf-8')
                
        except urllib.error.HTTPError as e:
            # HTTP error response (4xx, 5xx)
            raise HTTPError(e.code, e.reason)
            
        except urllib.error.URLError as e:
            # Network error (DNS, connection, etc.)
            if isinstance(e.reason, str) and 'timed out' in e.reason.lower():
                raise TimeoutError(f"Request timed out after {timeout_val}s")
            raise ConnectionError(f"Connection failed: {e.reason}")
            
        except Exception as e:
            # Other errors
            raise NetworkError(f"Request failed: {e}")


# Convenience singleton for simple usage
_default_client = None


def get_client(timeout=10.0) -> NetworkClient:
    """
    Get the default NetworkClient singleton.
    
    Args:
        timeout: Default timeout for requests
        
    Returns:
        NetworkClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = NetworkClient(timeout=timeout)
    return _default_client


# Convenience functions using default client
def get(url: str, callback: Callable[[TaskResult], None], **kwargs) -> None:
    """Perform async GET request using default client."""
    get_client().get(url, callback, **kwargs)


def get_json(url: str, callback: Callable[[TaskResult], None], **kwargs) -> None:
    """Perform async GET request and parse JSON using default client."""
    get_client().get_json(url, callback, **kwargs)


def post(url: str, data: Dict[str, Any], callback: Callable[[TaskResult], None], **kwargs) -> None:
    """Perform async POST request using default client."""
    get_client().post(url, data, callback, **kwargs)


def post_json(url: str, data: Dict[str, Any], callback: Callable[[TaskResult], None], **kwargs) -> None:
    """Perform async POST request and parse JSON using default client."""
    get_client().post_json(url, data, callback, **kwargs)
