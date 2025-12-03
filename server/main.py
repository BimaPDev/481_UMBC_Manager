import os
import io
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import generator
import config
from pydantic import BaseModel

class Settings(BaseModel):
    FORM_ID: str
    REF_SHEET_ID: str
    REF_SHEET_TAB: str
    TEMPLATE_DOC_ID: str
    OUTPUT_TITLE_PREFIX: str
    FOLDER_NAME: str

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/forms.body.readonly",
]

FOLDER_NAME = "CMSC-447-CS-Preadvising"

# --- AUTH HELPER ---
def get_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Requires credentials.json to be in the backend folder
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def get_or_create_folder(service, folder_name):
    # Check if folder exists
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    
    if files:
        return files[0]["id"]
    else:
        # Create folder
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        file = service.files().create(body=file_metadata, fields="id").execute()
        return file.get("id")

async def background_sync():
    """Runs the sync process every 60 seconds."""
    print("--- BACKGROUND SYNC STARTED ---")
    while True:
        try:
            print("--- RUNNING SYNC ---")
            # Run sync in a separate thread to avoid blocking the event loop
            creds = get_creds()
            service = build("drive", "v3", credentials=creds)
            target_folder_id = get_or_create_folder(service, FOLDER_NAME)
            
            await asyncio.to_thread(generator.process_and_create_docs, creds, target_folder_id)
            print("--- SYNC COMPLETE ---")
        except Exception as e:
            print(f"--- SYNC FAILED: {e} ---")
        
        await asyncio.sleep(60) # Wait for 60 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    task = asyncio.create_task(background_sync())
    yield
    # Cancel task on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("--- BACKGROUND SYNC STOPPED ---")

app = FastAPI(lifespan=lifespan)

# --- CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINT 1: SEARCH ---
@app.get("/search")
def search_docs(query: str):
    if not query: return []
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)
    safe_query = query.replace("'", "\\'")
    
    target_folder_id = get_or_create_folder(service, FOLDER_NAME)

    # Logic: Search Name BUT ONLY inside TARGET_FOLDER_ID
    drive_query = (
        f"'{target_folder_id}' in parents "
        f"and name contains '{safe_query}' "
        "and mimeType = 'application/vnd.google-apps.document' "
        "and trashed = false"
    )

    results = service.files().list(
        q=drive_query,
        pageSize=10,
        fields="nextPageToken, files(id, name, webViewLink, createdTime)"
    ).execute()

    return results.get("files", [])

# --- ENDPOINT 2: SYNC (GENERATE DOCS) ---
@app.post("/sync")
def trigger_sync():
    """
    Checks Google Forms for new submissions and creates Docs for them.
    """
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)
    target_folder_id = get_or_create_folder(service, FOLDER_NAME)
    
    # Calls the logic inside generator.py
    result = generator.process_and_create_docs(creds, target_folder_id)
    return result

# --- ENDPOINT 3: EXPORT (DOWNLOAD) ---
@app.get("/export/{file_id}")
def export_doc(file_id: str, mime_type: str):
    """
    Exports a Google Doc as PDF or DOCX and streams it to the client.
    """
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)

    # Map simple names to Google MIME types
    mime_map = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    google_mime = mime_map.get(mime_type)
import os
import io
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import generator
import config
from pydantic import BaseModel

class Settings(BaseModel):
    FORM_ID: str
    REF_SHEET_ID: str
    REF_SHEET_TAB: str
    TEMPLATE_DOC_ID: str
    OUTPUT_TITLE_PREFIX: str
    FOLDER_NAME: str

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/forms.body.readonly",
]

FOLDER_NAME = "CMSC-447-CS-Preadvising"

# --- AUTH HELPER ---
def get_creds():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Requires credentials.json to be in the backend folder
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def get_or_create_folder(service, folder_name):
    # Check if folder exists
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    
    if files:
        return files[0]["id"]
    else:
        # Create folder
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        file = service.files().create(body=file_metadata, fields="id").execute()
        return file.get("id")

async def background_sync():
    """Runs the sync process every 60 seconds."""
    print("--- BACKGROUND SYNC STARTED ---")
    while True:
        try:
            print("--- RUNNING SYNC ---")
            # Run sync in a separate thread to avoid blocking the event loop
            creds = get_creds()
            service = build("drive", "v3", credentials=creds)
            target_folder_id = get_or_create_folder(service, FOLDER_NAME)
            
            await asyncio.to_thread(generator.process_and_create_docs, creds, target_folder_id)
            print("--- SYNC COMPLETE ---")
        except Exception as e:
            print(f"--- SYNC FAILED: {e} ---")
        
        await asyncio.sleep(60) # Wait for 60 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    task = asyncio.create_task(background_sync())
    yield
    # Cancel task on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("--- BACKGROUND SYNC STOPPED ---")

app = FastAPI(lifespan=lifespan)

# --- CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINT 1: SEARCH ---
@app.get("/search")
def search_docs(query: str):
    if not query: return []
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)
    safe_query = query.replace("'", "\\'")
    
    target_folder_id = get_or_create_folder(service, FOLDER_NAME)

    # Logic: Search Name BUT ONLY inside TARGET_FOLDER_ID
    drive_query = (
        f"'{target_folder_id}' in parents "
        f"and name contains '{safe_query}' "
        "and mimeType = 'application/vnd.google-apps.document' "
        "and trashed = false"
    )

    results = service.files().list(
        q=drive_query,
        pageSize=10,
        fields="nextPageToken, files(id, name, webViewLink, createdTime)"
    ).execute()

    return results.get("files", [])

# --- ENDPOINT 2: SYNC (GENERATE DOCS) ---
@app.post("/sync")
def trigger_sync():
    """
    Checks Google Forms for new submissions and creates Docs for them.
    """
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)
    target_folder_id = get_or_create_folder(service, FOLDER_NAME)
    
    # Calls the logic inside generator.py
    result = generator.process_and_create_docs(creds, target_folder_id)
    return result

# --- ENDPOINT 3: EXPORT (DOWNLOAD) ---
@app.get("/export/{file_id}")
def export_doc(file_id: str, mime_type: str):
    """
    Exports a Google Doc as PDF or DOCX and streams it to the client.
    """
    creds = get_creds()
    service = build("drive", "v3", credentials=creds)

    # Map simple names to Google MIME types
    mime_map = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    google_mime = mime_map.get(mime_type)
    if not google_mime:
        raise HTTPException(status_code=400, detail="Unsupported format")

    try:
        # Request the export from Google
        request = service.files().export_media(fileId=file_id, mimeType=google_mime)
        file_stream = io.BytesIO()
        downloader = request.execute() # Executes and returns raw bytes

        file_stream.write(downloader)
        file_stream.seek(0)

        # Set filename for download
        filename = f"document.{mime_type}"
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}

        return StreamingResponse(file_stream, media_type=google_mime, headers=headers)

    except Exception as e:
        print(f"Export Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINT 4: SETTINGS ---
@app.get("/settings")
def get_settings():
    return config.load_config()

@app.post("/settings")
def update_settings(settings: Settings):
    updated = config.save_config(settings.dict())
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to save settings")
    return updated

if __name__ == "__main__":
    import uvicorn
    # Use "main:app" string to enable reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)