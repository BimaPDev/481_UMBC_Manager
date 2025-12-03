from googleapiclient.discovery import build
import json
import os
import config

# --- CONFIG ---
# Loaded dynamically from config.py
STATE_FILE = "state.json"

def dbg(tag, obj):
    try:
        print(f"\n[{tag}]")
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    except Exception:
        print(f"\n[{tag}] {obj}")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state: {e}")
    return {"processed_ids": []}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

def fetch_form_structure(svc_forms):
    # 1. Get Form Structure to map IDs to Titles
    cfg = config.load_config()
    try:
        form = svc_forms.forms().get(formId=cfg["FORM_ID"]).execute()
    except Exception as e:
        print(f"Error fetching form: {e}")
        return {}

    id_to_title = {}
    for item in form.get("items", []):
        qi = item.get("questionItem", {})
        q = qi.get("question", {})
        if "questionId" in q:
            id_to_title[q["questionId"]] = item["title"]
    return id_to_title

def fetch_form_responses(svc_forms):
    cfg = config.load_config()
    id_to_title = fetch_form_structure(svc_forms)
    
    # 2. Get Responses
    try:
        resp = svc_forms.forms().responses().list(formId=cfg["FORM_ID"]).execute()
    except Exception as e:
        print(f"Error fetching responses: {e}")
        return []

    out = []
    for r in resp.get("responses", []):
        row = {}
        # Store the responseId to track state
        row["_responseId"] = r.get("responseId")
        
        for qid, ans in r.get("answers", {}).items():
            key = id_to_title.get(qid, qid)
            # Join multiple answers with newlines
            vals = [a.get("value", "") for a in ans.get("textAnswers", {}).get("answers", [])]
            row[key] = "\n".join(vals)
        out.append(row)
    return out

def read_sheet_as_dicts(svc_sheets, sheet_id: str, tab: str):
    rng = f"{tab}!A1:B"
    try:
        res = svc_sheets.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=rng
        ).execute()
        values = res.get("values", []) or []
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return [], []

    # If first row looks like real headers (non-numeric/wordy), use them.
    def looks_like_headers(row):
        if not row: return False
        # treat as headers if at least one cell has non-digit and length > 1
        for c in row[:2]:
            if c and (not str(c).strip().isdigit()) and len(str(c).strip()) > 1:
                return True
        return False

    rows = []
    headers = ["Number", "Letter"]
    if values and looks_like_headers(values[0]):
        headers = values[0]
        data = values[1:]
        for r in data:
            rows.append({
                headers[0]: (r[0] if len(r) > 0 else ""),
                headers[1]: (r[1] if len(r) > 1 else ""),
            })
    else:
        # No headers -> synthesize
        for r in values:
            num = r[0] if len(r) > 0 else ""
            let = r[1] if len(r) > 1 else ""
            rows.append({"Number": str(num), "Letter": str(let)})
            
    return headers, rows

def process_and_create_docs(creds, folder_id):
    svc_forms = build("forms", "v1", credentials=creds)
    svc_docs = build("docs", "v1", credentials=creds)
    svc_drive = build("drive", "v3", credentials=creds)
    svc_sheets = build("sheets", "v4", credentials=creds)

    print("\n=== START SYNC ===")
    
    cfg = config.load_config()
    
    # Load state
    state = load_state()
    processed_ids = set(state.get("processed_ids", []))
    print(f"Loaded state: {len(processed_ids)} processed responses.")
    
    # Read Reference Sheet (as requested to keep track of things)
    _, ref_rows = read_sheet_as_dicts(svc_sheets, cfg["REF_SHEET_ID"], cfg["REF_SHEET_TAB"])
    print(f"Reference rows count: {len(ref_rows)}")

    responses = fetch_form_responses(svc_forms)
    print(f"Total form responses found: {len(responses)}")
    
    generated_count = 0
    
    # 3. Process Responses
    for row in responses:
        response_id = row.get("_responseId")
        
        if response_id in processed_ids:
            # Skip already processed
            continue
            
        first = row.get("First Name", "")
        last = row.get("Last Name", "")
        # Use Preferred First Name if available
        pref = row.get("Preferred First Name", "")
        name_display = pref or first or "(No Name)"
        
        extra = row.get("What additional information are you interested in learning more about (check all that apply)?", "")
        
        # Replacements matching the reference code logic
        replacements = {
            "Academic Resources": "\nAcademic Resources:\n https://academicsuccess.umbc.edu/academic-learning-resources/\n",
            "Experiential Learning": "\nExperiential Learning:\n https://civiclife.umbc.edu/learning-engagement/\n",
            "Financial Aid": "\nFinancial Aid:\n https://financialaid.umbc.edu/",
            "Transfer Scholars Programs & Scholarships": "\nTransfer Scholars Programs & Scholarships:\n https://scholarships.umbc.edu/freshmen/\n",
            "Pre-Professional Programs (Pre-Med, Pre-Dental, Pre-Law, etc.)": "\nPre-Professional Programs (Pre-Med, Pre-Dental, Pre-Law, etc.):\n https://umbc.edu/programs/undergraduate/pre-professional-programs/\n",
            "The Honors College": "\nThe Honors College:\n https://honors.umbc.edu/\n",
            "Transfer Student Alliance (TSA) Program": "\nTransfer Student Alliance (TSA) Program:\n https://umbc.edu/undergraduate/transfer-students/tsa/\n",
            "Campus Housing (Catonsille location only)": "\nCampus Housing (Catonsville location only):\n https://reslife.umbc.edu/apply/\n",
            "Pre-Transfer Programs (Summer Transfer Institute, Semester Meet-Ups, etc.)": "\nPre-Transfer Programs (Summer Transfer Institute, Semester Meet-Ups, etc.):\n https://advising.coeit.umbc.edu/pre-transfer-advising/\n",
            "Veteran Student Information": "\nVeteran Student Information:\n https://umbc.edu/undergraduate/veteran-students/\n",
            "COEIT Student Clubs & Organizations": "\nCOEIT Student Clubs & Organizations:\n https://advising.coeit.umbc.edu/coeit-student-organizations/\n",
            "Student Disability Services": "\nStudent Disability Services:\n https://sds.umbc.edu/\n",
            "Career/Educational Goals": "\nCareer/Educational Goals:\n https://careers.umbc.edu/aboutus/outcomes/\n",
            "Information Systems Mentoring Program": "\nInformation Systems Mentoring Program:\n https://cwit.umbc.edu/peermentoring/\n",
            "Credit When It’s Due Program: Reverse Awarding of the Associate’s Degree": "\nCredit When It's Due Program: Reverse Awarding of the Associate's Degree:\n https://reverseaward.umbc.edu/",
        }
    
        for k, v in replacements.items():
            extra = extra.replace(k, v)
    
        new_title = f"{cfg['OUTPUT_TITLE_PREFIX']}{last}, {name_display}"
            
        # 4. Check if file exists specifically inside TARGET_FOLDER
        query = f"name = '{new_title}' and '{folder_id}' in parents and trashed = false"
        existing = svc_drive.files().list(q=query).execute().get('files', [])
            
        if not existing:
            print(f"Generating: {new_title}")
            # 5. Copy Template INTO the target folder
            copy_body = {
                "name": new_title,
                "parents": [folder_id]
            }
            copied_file = svc_drive.files().copy(fileId=cfg['TEMPLATE_DOC_ID'], body=copy_body).execute()
            new_id = copied_file["id"]
    
            # 6. Insert Text
            full_doc = svc_docs.documents().get(documentId=new_id).execute()
            content = full_doc.get("body", {}).get("content", [])
            end_index = content[-1]["endIndex"] - 1 if content else 1
    
            svc_docs.documents().batchUpdate(
                documentId=new_id,
                body={"requests": [{"insertText": {"location": {"index": end_index}, "text": extra}}]}
            ).execute()
            generated_count += 1
            print(f"New Doc: https://docs.google.com/document/d/{new_id}")
            
            # Update state
            if response_id:
                processed_ids.add(response_id)
                save_state({"processed_ids": list(processed_ids)})
        else:
            print(f"Skipping: {new_title} (Already exists)")
            # Even if it exists, mark as processed so we don't check it every time? 
            # Or should we re-check? Let's mark it to be safe and efficient.
            if response_id:
                processed_ids.add(response_id)
                save_state({"processed_ids": list(processed_ids)})
    
    print("=== END SYNC ===")
    return {"status": "success", "generated": generated_count}