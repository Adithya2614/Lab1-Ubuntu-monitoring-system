from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controller.api.router import router

app = FastAPI(title="Ubuntu Monitoring Controller", version="1.0.0")

# Configure CORS for Dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. In production, restrict to dashboard URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    from controller.services.ansible_service import AnsibleService
    AnsibleService.start_background_polling()
    AnsibleService.start_background_time_sync()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Ubuntu Monitoring Controller"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("controller.main:app", host="0.0.0.0", port=8000, reload=True)
