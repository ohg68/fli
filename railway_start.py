"""Railway entry point with CORS support."""
import os
import uvicorn
from fli.mcp.server import mcp
from starlette.middleware.cors import CORSMiddleware

app = mcp.http_app(path="/mcp")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host=host, port=port)
