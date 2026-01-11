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
    # Startup
    await db.connect_db()
    app.state.router = RouterAgent(db.db)
    await app.state.router.initialize_bots()
    yield
    # Shutdown
    await db.close_db()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/route")
async def route_query(
    request: Request,
    prompt: str = Form(...),
    file: UploadFile = File(None)
):
    # Get user_id and convo_id from cookies or generate new
    user_id = request.cookies.get("user_id", str(uuid.uuid4()))
    convo_id = request.cookies.get("convo_id", str(uuid.uuid4()))

    file_path = None
    if file:
        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    try:
        result = await app.state.router.route(prompt, user_id, convo_id, file_path)
        
        text = result.get("text", "")
        pdf_file = result.get("pdf_file", None)

        resp = None
        if text and pdf_file:
            # Multipart response for both text and PDF
            if isinstance(text, list):
                text_str = "\n".join(text)
            else:
                text_str = str(text)

            pdf_file.seek(0)
            pdf_bytes = pdf_file.read()
            boundary = "----Boundary"
            
            parts = [
                f'--{boundary}\r\nContent-Type: application/json\r\n\r\n{json.dumps({"text": text_str})}\r\n'.encode('utf-8'),
                f'--{boundary}\r\nContent-Type: application/pdf\r\nContent-Disposition: attachment; filename=result.pdf\r\n\r\n'.encode('utf-8') + pdf_bytes,
                f'\r\n--{boundary}--\r\n'.encode('utf-8')
            ]
            body = b''.join(parts)
            resp = Response(content=body, media_type=f'multipart/mixed; boundary={boundary}')
        
        elif pdf_file:
            resp = StreamingResponse(pdf_file, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=result.pdf"})
        
        else:
            resp = JSONResponse({"text": text})

        # Set cookies
        resp.set_cookie(key="user_id", value=user_id, max_age=86400, samesite="None", secure=True, path="/")
        resp.set_cookie(key="convo_id", value=convo_id, max_age=86400, samesite="None", secure=True, path="/")
        
        return resp

    except Exception as e:
        print(f"Error in route_query: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        if file_path and os.path.exists(file_path):
            # os.remove(file_path) # Might want to keep it if processing is async, but here it's sync-ish
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
