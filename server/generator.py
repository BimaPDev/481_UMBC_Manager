from googleapiclient.discovery import build # Bima worked on this
 # Bima worked on this
# --- CONFIG --- # Bima worked on this
FORM_ID = "17aGxa61B0h_YjCJQAGLu4e0Q9kzLzt4eLzSevoi7M9Q" # Bima worked on this
TEMPLATE_DOC_ID = "1jqfnp7MuszXsgbosCCWWCs8AaZNyDKHa4n1zWthFRCg" # Bima worked on this
OUTPUT_TITLE_PREFIX = "Computer Science 4 Year Plan: " # Bima worked on this
TARGET_FOLDER_ID = "1XHoiWkH7x3YtoQiMQbE-vavkCooctjnr" # Bima worked on this
 # Bima worked on this
def fetch_form_responses(svc_forms): # Bima worked on this
    # 1. Get Form Structure to map IDs to Titles # Bima worked on this
    try: # Bima worked on this
        form = svc_forms.forms().get(formId=FORM_ID).execute() # Bima worked on this
    except Exception as e: # Bima worked on this
        print(f"Error fetching form: {e}") # Bima worked on this
        return [] # Bima worked on this
 # Bima worked on this
    id_to_title = {} # Bima worked on this
    for item in form.get("items", []): # Bima worked on this
        qi = item.get("questionItem", {}) # Bima worked on this
        q = qi.get("question", {}) # Bima worked on this
        if "questionId" in q: # Bima worked on this
            id_to_title[q["questionId"]] = item["title"] # Bima worked on this
 # Bima worked on this
    # 2. Get Responses # Bima worked on this
    resp = svc_forms.forms().responses().list(formId=FORM_ID).execute() # Bima worked on this
    out = [] # Bima worked on this
    for r in resp.get("responses", []): # Bima worked on this
        row = {} # Bima worked on this
        for qid, ans in r.get("answers", {}).items(): # Bima worked on this
            key = id_to_title.get(qid, qid) # Bima worked on this
            # Join multiple answers with newlines # Bima worked on this
            vals = [a.get("value", "") for a in ans.get("textAnswers", {}).get("answers", [])] # Bima worked on this
            row[key] = "\n".join(vals) # Bima worked on this
        out.append(row) # Bima worked on this
    return out # Bima worked on this
 # Bima worked on this
def process_and_create_docs(creds): # Bima worked on this
    svc_forms = build("forms", "v1", credentials=creds) # Bima worked on this
    svc_docs = build("docs", "v1", credentials=creds) # Bima worked on this
    svc_drive = build("drive", "v3", credentials=creds) # Bima worked on this
 # Bima worked on this
    responses = fetch_form_responses(svc_forms) # Bima worked on this
    generated_count = 0 # Bima worked on this
     # Bima worked on this
    # 3. Process Responses # Bima worked on this
    for row in responses: # Bima worked on this
        first = row.get("First Name", "") # Bima worked on this
        last = row.get("Last Name", "") # Bima worked on this
        extra = row.get("What additional information are you interested in learning more about (check all that apply)?", "") # Bima worked on this
         # Bima worked on this
        # Mapping for the additional info links # Bima worked on this
        replacements = { # Bima worked on this
            "Academic Resources": "\nAcademic Resources:\n https://academicsuccess.umbc.edu/academic-learning-resources/",  # Bima worked on this
            "Experiential Learning": "\nExperiential Learning:\n https://civiclife.umbc.edu/learning-engagement/",# Bima worked on this
            "Financial Aid": "\nFinancial Aid:\n https://financialaid.umbc.edu/",# Bima worked on this
            "Transfer Scholars Programs & Scholarships": "\nTransfer Scholars Programs & Scholarships:\n https://scholarships.umbc.edu/freshmen/",# Bima worked on this
            "Pre-Professional Programs (Pre-Med, Pre-Dental, Pre-Law, etc.)": "\nPre-Professional Programs (Pre-Med, Pre-Dental, Pre-Law, etc.):\n https://umbc.edu/programs/undergraduate/pre-professional-programs/",# Bima worked on this
            "The Honors College": "\nThe Honors College:\n https://honors.umbc.edu/",# Bima worked on this
            "Transfer Student Alliance (TSA) Program": "\nTransfer Student Alliance (TSA) Program:\n https://umbc.edu/undergraduate/transfer-students/tsa/",# Bima worked on this
            "Campus Housing (Catonsille location only)": "\nCampus Housing (Catonsville location only):\n https://reslife.umbc.edu/apply/",# Bima worked on this
            "Pre-Transfer Programs (Summer Transfer Institute, Semester Meet-Ups, etc.)": "\nPre-Transfer Programs (Summer Transfer Institute, Semester Meet-Ups, etc.):\n https://advising.coeit.umbc.edu/pre-transfer-advising/",# Bima worked on this
            "Veteran Student Information": "\nVeteran Student Information:\n https://umbc.edu/undergraduate/veteran-students/",# Bima worked on this
            "COEIT Student Clubs & Organizations": "\nCOEIT Student Clubs & Organizations:\n https://advising.coeit.umbc.edu/coeit-student-organizations/",# Bima worked on this
            "Student Disability Services": "\nStudent Disability Services:\n https://sds.umbc.edu/",# Bima worked on this
            "Career/Educational Goals": "\nCareer/Educational Goals:\n https://careers.umbc.edu/aboutus/outcomes/",# Bima worked on this
            "Information Systems Mentoring Program": "\nInformation Systems Mentoring Program:\n https://cwit.umbc.edu/peermentoring/",# Bima worked on this
            "Credit When It’s Due Program: Reverse Awarding of the Associate’s Degree": "\nCredit When It's Due Program: Reverse Awarding of the Associate's Degree:\n https://reverseaward.umbc.edu/"# Bima worked on this
        }   # Bima Worked On This
    # Bima Worked On This
        for k, v in replacements.items():   # Bima Worked On This
            extra = extra.replace(k, v) # Bima Worked On This
    # Bima Worked On This
        new_title = f"{OUTPUT_TITLE_PREFIX}{last}, {first}" # Bima Worked On This
            # Bima Worked On This
        # 4. Check if file exists specifically inside TARGET_FOLDER # Bima Worked On This
        query = f"name = '{new_title}' and '{TARGET_FOLDER_ID}' in parents and trashed = false" # Bima Worked On This
        existing = svc_drive.files().list(q=query).execute().get('files', [])   # Bima Worked On This
            # Bima Worked On This
        if not existing:    # Bima Worked On This
            print(f"Generating: {new_title}")   # Bima Worked On This
            # 5. Copy Template INTO the target folder   # Bima Worked On This
            copy_body = {   # Bima Worked On This
                "name": new_title,  # Bima Worked On This
                "parents": [TARGET_FOLDER_ID]   # Bima Worked On This
            }   # Bima Worked On This
            copied_file = svc_drive.files().copy(fileId=TEMPLATE_DOC_ID, body=copy_body).execute()  # Bima Worked On This
            new_id = copied_file["id"]  # Bima Worked On This
    # Bima Worked On This
            # 6. Insert Text    # Bima Worked On This
            full_doc = svc_docs.documents().get(documentId=new_id).execute()    # Bima Worked On This
            content = full_doc.get("body", {}).get("content", [])   # Bima Worked On This
            end_index = content[-1]["endIndex"] - 1 if content else 1   # Bima Worked On This
    # Bima Worked On This
            svc_docs.documents().batchUpdate(   # Bima Worked On This
                documentId=new_id,  # Bima Worked On This
                body={"requests": [{"insertText": {"location": {"index": end_index}, "text": extra}}]}  # Bima Worked On This
            ).execute() # Bima Worked On This
            generated_count += 1    # Bima Worked On This
        else:   # Bima Worked On This
            print(f"Skipping: {new_title} (Already exists)")    # Bima Worked On This
    # Bima Worked On This
    return {"status": "success", "generated": generated_count}  # Bima Worked On This