export interface DriveFile {
  id: string;
  name: string;
  webViewLink: string;
  createdTime: string;
}

export interface Settings {
  FORM_ID: string;
  REF_SHEET_ID: string;
  REF_SHEET_TAB: string;
  TEMPLATE_DOC_ID: string;
  OUTPUT_TITLE_PREFIX: string;
  FOLDER_NAME: string;
}
