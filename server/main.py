import os   # Bima Worked On this
import io   # Bima Worked On this
from fastapi import FastAPI, HTTPException   # Bima Worked On this
from fastapi.middleware.cors import CORSMiddleware   # Bima Worked On this
from fastapi.responses import StreamingResponse   # Bima Worked On this
from google.oauth2.credentials import Credentials   # Bima Worked On this
from google_auth_oauthlib.flow import InstalledAppFlow   # Bima Worked On this
from google.auth.transport.requests import Request   # Bima Worked On this
from googleapiclient.discovery import build   # Bima Worked On this
import generator    # Bima Worked On this
   # Bima Worked On this
app = FastAPI()   # Bima Worked On this

# --- CONFIGURATION ---     #Bima Worked on this
app.add_middleware( #Bima Worked on this
    CORSMiddleware, #Bima Worked on this
    allow_origins=["http://localhost:5173"],    #Bima Worked on this
    allow_credentials=True, #Bima Worked on this
    allow_methods=["*"],    #Bima Worked on this
    allow_headers=["*"],    #Bima Worked on this
)   #Bima Worked on this
    #Bima Worked on this
SCOPES = [  #Bima Worked on this
    "https://www.googleapis.com/auth/drive",    #Bima Worked on this
    "https://www.googleapis.com/auth/spreadsheets", #Bima Worked on this
    "https://www.googleapis.com/auth/documents",    #Bima Worked on this
    "https://www.googleapis.com/auth/forms.responses.readonly", #Bima Worked on this
]   #Bima Worked on this
    #Bima Worked on this
# TARGET FOLDER ID (Must match generator.py)    #Bima Worked on this
TARGET_FOLDER_ID = "1XHoiWkH7x3YtoQiMQbE-vavkCooctjnr"  #Bima Worked on this
    #Bima Worked on this
# --- AUTH HELPER ---   #Bima Worked on this
def get_creds():    #Bima Worked on this
    creds = None    #Bima Worked on this
    if os.path.exists("token.json"):    #Bima Worked on this
        creds = Credentials.from_authorized_user_file("token.json", SCOPES) #Bima Worked on this
    if not creds or not creds.valid:    #Bima Worked on this
        if creds and creds.expired and creds.refresh_token: #Bima Worked on this
            creds.refresh(Request())    #Bima Worked on this
        else:   #Bima Worked on this
            # Requires credentials.json to be in the backend folder #Bima Worked on this
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)    #Bima Worked on this
            creds = flow.run_local_server(port=8080)    #Bima Worked on this
        with open("token.json", "w") as f:  #Bima Worked on this
            f.write(creds.to_json())    #Bima Worked on this
    return creds    #Bima Worked on this
    #Bima Worked on this
# --- ENDPOINT 1: SEARCH ---    #Bima Worked on this
@app.get("/search") #Bima Worked on this
def search_docs(query: str):    #Bima Worked on this
    if not query: return [] #Bima Worked on this
    creds = get_creds() #Bima Worked on this
    service = build("drive", "v3", credentials=creds)   #Bima Worked on this
    safe_query = query.replace("'", "\\'")  #Bima Worked on this
        #Bima Worked on this
    # Logic: Search Name/Content BUT ONLY inside TARGET_FOLDER_ID   #Bima Worked on this
    drive_query = ( #Bima Worked on this
        f"'{TARGET_FOLDER_ID}' in parents " #Bima Worked on this
        f"and (name contains '{safe_query}' or fullText contains '{safe_query}') "  #Bima Worked on this
        "and mimeType = 'application/vnd.google-apps.document' "    #Bima Worked on this
        "and trashed = false"   #Bima Worked on this
    )   #Bima Worked on this
    #Bima Worked on this
    results = service.files().list( #Bima Worked on this
        q=drive_query,  #Bima Worked on this
        pageSize=10,    #Bima Worked on this
        fields="nextPageToken, files(id, name, webViewLink, createdTime)"   #Bima Worked on this
    ).execute() #Bima Worked on this
    #Bima Worked on this
    return results.get("files", []) #Bima Worked on this
    #Bima Worked on this
# --- ENDPOINT 2: SYNC (GENERATE DOCS) ---  #Bima Worked on this
@app.post("/sync")  #Bima Worked on this
def trigger_sync(): #Bima Worked on this
    """ #Bima Worked on this
    Checks Google Forms for new submissions and creates Docs for them.  #Bima Worked on this
    """ #Bima Worked on this
    creds = get_creds() #Bima Worked on this
    # Calls the logic inside generator.py   #Bima Worked on this
    result = generator.process_and_create_docs(creds)   #Bima Worked on this
    return result   #Bima Worked on this
    #Bima Worked on this
# --- ENDPOINT 3: EXPORT (DOWNLOAD) --- #Bima Worked on this
@app.get("/export/{file_id}")   #Bima Worked on this
def export_doc(file_id: str, mime_type: str):   #Bima Worked on this
    """ #Bima Worked on this
    Exports a Google Doc as PDF or DOCX and streams it to the client.   #Bima Worked on this
    """ #Bima Worked on this
    creds = get_creds() #Bima Worked on this
    service = build("drive", "v3", credentials=creds)   #Bima Worked on this
    #Bima Worked on this
    # Map simple names to Google MIME types #Bima Worked on this
    mime_map = {    #Bima Worked on this
        "pdf": "application/pdf",   #Bima Worked on this
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"   #Bima Worked on this
    }   #Bima Worked on this
        #Bima Worked on this
    google_mime = mime_map.get(mime_type)   #Bima Worked on this
    if not google_mime: #Bima Worked on this
        raise HTTPException(status_code=400, detail="Unsupported format")   #Bima Worked on this
    #Bima Worked on this
    try:    #Bima Worked on this
        # Request the export from Google    #Bima Worked on this
        request = service.files().export_media(fileId=file_id, mimeType=google_mime)    #Bima Worked on this
        file_stream = io.BytesIO()  #Bima Worked on this
        downloader = request.execute() # Executes and returns raw bytes #Bima Worked on this
            #Bima Worked on this
        file_stream.write(downloader)   #Bima Worked on this
        file_stream.seek(0) #Bima Worked on this
            #Bima Worked on this
        # Set filename for download #Bima Worked on this
        filename = f"document.{mime_type}"  #Bima Worked on this
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'} #Bima Worked on this
            #Bima Worked on this
        return StreamingResponse(file_stream, media_type=google_mime, headers=headers)  #Bima Worked on this
            #Bima Worked on this
    except Exception as e:  #Bima Worked on this
        print(f"Export Error: {e}") #Bima Worked on this
        raise HTTPException(status_code=500, detail=str(e)) #Bima Worked on this
    #Bima Worked on this
if __name__ == "__main__":  #Bima Worked on this
    import uvicorn  #Bima Worked on this
    uvicorn.run(app, host="0.0.0.0", port=8000) #Bima Worked on this