from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .routes import search, spare_parts

# Create FastAPI app instance
app = FastAPI(
    title="Intent-Based Search and Recommendation System",
    description="An AI-powered search system that understands user intent and handles dependencies",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(spare_parts.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/spare-parts")
async def spare_parts_page(request: Request):
    return templates.TemplateResponse("spare_parts.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Service is running"}

# Keep the old API docs available at /docs
@app.get("/api-docs")
async def redirect_to_docs():
    """Redirect to API documentation"""
    return {"message": "API docs available at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)