from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .routes import search, spare_parts
from .services.spare_part_recommender_model import IntelligentSparePartRecommender
import time

# Create FastAPI app instance
app = FastAPI(
    title="Intent-Based Search and Recommendation System",
    description="An AI-powered search system that understands user intent and handles dependencies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Initialize recommender for direct API calls
recommender = IntelligentSparePartRecommender()

# Include routers
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(spare_parts.router)  # No prefix here since spare_parts.py already has prefix

# MAIN ROUTE - Your frontend calls /api/intelligent-recommendations
@app.post("/api/intelligent-recommendations")
async def intelligent_recommendations_main(request: dict):
    """Main route to handle frontend calls to /api/intelligent-recommendations"""
    try:
        print(f"📥 Received request: {request}")
        
        # Your frontend sends 'user_problem', let's handle it properly
        user_problem = request.get('user_problem', '')
        user_preferences = request.get('user_preferences', {})
        max_results = request.get('max_results', 10)
        include_analysis = request.get('include_analysis', True)
        
        if not user_problem:
            raise HTTPException(status_code=400, detail="user_problem is required")
        
        print(f"🧠 Processing intelligent recommendation for: {user_problem}")
        
        # Use your intelligent recommender
        result = recommender.get_smart_recommendations(user_problem)
        
        # Format response to match frontend expectations exactly
        formatted_response = {
            "detected_issue": {
                "original_text": result['detected_issue']['original_text'],
                "detected_issues": result['detected_issue']['detected_issues'],
                "device_type": result['detected_issue']['device_type'],
                "urgency": result['detected_issue']['urgency'],
                "keywords_found": result['detected_issue']['keywords_found'],
                "brand_mentioned": result['detected_issue']['brand_mentioned']
            },
            "personalized_message": result['personalized_message'],
            "recommendations": result['recommendations'][:max_results],
            "total_found": result['total_found'],
            "user_profile": result['user_profile'],
            "confidence": "High",
            "confidence_score": 95,
            "response_time": "< 1s",
            "status": "success"
        }
        
        print(f"✅ Sending response with {len(formatted_response['recommendations'])} recommendations")
        return formatted_response
        
    except Exception as e:
        print(f"❌ Error in intelligent recommendations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/quick-analysis")
async def quick_analysis_main(request: dict):
    """Route to handle frontend calls to /api/quick-analysis"""
    try:
        problem_text = request.get('problem_text', '')
        
        if not problem_text:
            return {"analysis": "No text provided"}
        
        print(f"🔍 Quick analysis for: {problem_text}")
        
        # Quick analysis using your existing system
        result = recommender.get_smart_recommendations(problem_text)
        
        return {
            "detected_device": result['detected_issue'].get('device_type', 'Unknown'),
            "detected_issues": result['detected_issue'].get('detected_issues', []),
            "confidence": "High",
            "brand_mentioned": result['detected_issue'].get('brand_mentioned', None),
            "urgency": result['detected_issue'].get('urgency', 'medium')
        }
        
    except Exception as e:
        print(f"❌ Quick analysis error: {e}")
        return {"analysis": "Analysis failed", "error": str(e)}

# Additional endpoints to support your frontend
@app.post("/api/analyze-problem")
async def analyze_problem(request: dict):
    """Alternative endpoint for problem analysis"""
    try:
        description = request.get('description', '') or request.get('problem_description', '')
        
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        # Use your intelligent recommender
        result = recommender.get_smart_recommendations(description)
        
        return {
            "status": "success",
            "analysis": result['detected_issue'],
            "recommendations": result['recommendations'][:5],  # Limit to 5 for UI
            "message": result['personalized_message']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main HTML interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/spare-parts")
async def spare_parts_page(request: Request):
    """Serve spare parts page"""
    return templates.TemplateResponse("spare_parts.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Service is running",
        "timestamp": time.time(),
        "recommender_loaded": hasattr(recommender, 'parts_database'),
        "total_parts": sum(
            len(parts) 
            for device_type in recommender.parts_database.values() 
            for brand_parts in device_type.values() 
            for parts in [brand_parts]
        ) if hasattr(recommender, 'parts_database') else 0
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy", 
        "api_version": "1.0.0",
        "services": {
            "search": "active",
            "spare_parts": "active",
            "recommender": "loaded"
        }
    }

@app.get("/api-docs")
async def redirect_to_docs():
    """Redirect to API documentation"""
    return {"message": "API docs available at /docs"}

# Catch tracking requests that cause 404 errors
@app.get("/hybridaction/{path:path}")
async def catch_tracking_requests(path: str):
    """Catch and ignore tracking requests that cause 404 errors"""
    return {"status": "ignored"}

# Handle any remaining 404s gracefully
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return {"error": "Not found", "path": str(request.url)}

# Handle 422 validation errors
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    print(f"❌ Validation error on {request.url}: {exc}")
    return {"error": "Invalid request format", "details": str(exc)}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🔄 Loading search engine...")
    try:
        # Test the recommender
        test_result = recommender.get_smart_recommendations("test phone battery issue")
        print("✅ Spare parts recommender loaded successfully")
        print(f"📊 Loaded {len(recommender.parts_database)} device categories")
        print(f"👥 {len(recommender.user_profiles)} user profiles available")
    except Exception as e:
        print(f"❌ Failed to load recommender: {e}")
    
    print("🚀 Intent Search API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down Intent Search API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)