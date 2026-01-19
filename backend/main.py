import os
import uuid
import json
import shutil
from fastapi import FastAPI, File, UploadFile, Form, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from core.database import db
from core.config import Config
from services.router_agent import RouterAgent
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate configuration before startup
    config_errors = Config.validate()
    if config_errors:
        for error in config_errors:
            print(f"CONFIGURATION ERROR: {error}")
        raise RuntimeError("Missing required environment variables. Check your .env file.")
    
    # Startup
    await db.connect_db()
    app.state.router = RouterAgent(db.db)
    await app.state.router.initialize_bots()
    print("NEXUS Backend started successfully!")
    yield
    # Shutdown
    await db.close_db()
    # Cleanup temp directory on shutdown
    if os.path.exists("temp"):
        shutil.rmtree("temp", ignore_errors=True)
    print("NEXUS Backend shutdown complete.")

app = FastAPI(
    title="NEXUS API",
    description="AI Academic Tutor for IITI Community",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        # Add production URLs here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "NEXUS API"}

@app.post("/route")
async def route_query(
    request: Request,
    prompt: str = Form(...),
    file: UploadFile = File(None)
):
    """Main endpoint for routing user queries to appropriate bots."""
    # Get user_id and convo_id from cookies or generate new
    user_id = request.cookies.get("user_id", str(uuid.uuid4()))
    convo_id = request.cookies.get("convo_id", str(uuid.uuid4()))

    file_path = None
    if file and file.filename:
        os.makedirs("temp", exist_ok=True)
        # Use unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join("temp", unique_filename)
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            print(f"Error saving file: {e}")
            return JSONResponse(
                {"text": "Error uploading file. Please try again."},
                status_code=400
            )

    try:
        result = await app.state.router.route(prompt, user_id, convo_id, file_path)
        
        # Handle None result
        if result is None:
            result = {"text": "I'm having trouble processing your request. Please try again.", "pdf_file": None}
        
        text = result.get("text", "")
        pdf_file = result.get("pdf_file", None)

        resp = None
        if text and pdf_file:
            # Multipart response for both text and PDF
            if isinstance(text, list):
                text_str = "\n".join(text)
            else:
                text_str = str(text)

            try:
                pdf_file.seek(0)
                pdf_bytes = pdf_file.read()
            except Exception as e:
                print(f"Error reading PDF file: {e}")
                # Fall back to text-only response
                return JSONResponse({"text": text_str})
            
            boundary = "----Boundary"
            
            parts = [
                f'--{boundary}\r\nContent-Type: application/json\r\n\r\n{json.dumps({"text": text_str})}\r\n'.encode('utf-8'),
                f'--{boundary}\r\nContent-Type: application/pdf\r\nContent-Disposition: attachment; filename=result.pdf\r\n\r\n'.encode('utf-8') + pdf_bytes,
                f'\r\n--{boundary}--\r\n'.encode('utf-8')
            ]
            body = b''.join(parts)
            resp = Response(content=body, media_type=f'multipart/mixed; boundary={boundary}')
        
        elif pdf_file:
            try:
                pdf_file.seek(0)
                resp = StreamingResponse(pdf_file, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=result.pdf"})
            except Exception as e:
                print(f"Error streaming PDF: {e}")
                return JSONResponse({"text": "Error generating PDF. Please try again."}, status_code=500)
        
        else:
            resp = JSONResponse({"text": text})

        # Set cookies - use secure=False for local development (DEBUG mode)
        cookie_secure = not Config.DEBUG
        cookie_samesite = "None" if cookie_secure else "Lax"
        resp.set_cookie(key="user_id", value=user_id, max_age=86400, samesite=cookie_samesite, secure=cookie_secure, path="/")
        resp.set_cookie(key="convo_id", value=convo_id, max_age=86400, samesite=cookie_samesite, secure=cookie_secure, path="/")
        
        return resp

    except Exception as e:
        print(f"Error in route_query: {e}")
        return JSONResponse(
            {"text": "I encountered an unexpected error. Please try again or rephrase your question."},
            status_code=500
        )
    finally:
        # Clean up uploaded file after processing
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error cleaning up file {file_path}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

