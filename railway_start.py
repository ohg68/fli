"""Railway entry point with CORS support."""
import os
import uvicorn
from fli.mcp.server import mcp
from starlette.middleware.cors import CORSMiddleware

app = mcp.http_app(path="/mcp")

cors_app = CORSMiddleware(
    app,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Mcp-Session-Id"],
)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(cors_app, host=host, port=port)
