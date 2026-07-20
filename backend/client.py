import httpx

# Cache the original httpx.AsyncClient to prevent circular monkey-patching bugs
OriginalAsyncClient = httpx.AsyncClient

client = OriginalAsyncClient(
    timeout=15,
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=50)
)

class SharedClientContext:
    def __init__(self, *args, **kwargs):
        self.headers = kwargs.get("headers", {})
        
    async def __aenter__(self):
        if self.headers:
            # Dynamically update the shared client's headers for this block context
            client.headers.update(self.headers)
        return client
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
