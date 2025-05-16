# main.py - Application entry point and configuration
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from sneakers import router as sneakers_router

app = FastAPI(title="Sneaker MCP API")

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add a route to serve the HTML file
@app.get("/", response_class=FileResponse)
async def get_ui():
    return FileResponse("static/index.html")

# Register routers/blueprints
app.include_router(sneakers_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)