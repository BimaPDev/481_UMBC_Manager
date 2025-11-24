import { type DriveFile } from "../types";

interface Props {
  file: DriveFile;
  onBack: () => void;
}

export default function DocWorkspace({ file, onBack }: Props) {
  const handleDownload = (format: "pdf" | "docx") => {
    // We open the backend URL in a new window/tab to trigger browser download
    window.open(
      `http://localhost:8000/export/${file.id}?mime_type=${format}`,
      "_blank"
    );
  };

  return (
    <div style={{ height: "80vh", display: "flex", flexDirection: "column" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "10px",
        }}
      >
        <button onClick={onBack}>&larr; Back to Search</button>
        <h3>Editing: {file.name}</h3>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={() => handleDownload("pdf")}
            style={{ backgroundColor: "#dc3545" }}
          >
            Export PDF
          </button>
          <button
            onClick={() => handleDownload("docx")}
            style={{ backgroundColor: "#28a745" }}
          >
            Export Word
          </button>
        </div>
      </div>

      {/* The iframe embeds the Google Doc. 
        Google automatically handles the "Editor" UI if the user is logged in. 
      */}
      <iframe
        src={file.webViewLink}
        style={{ width: "100%", flex: 1, border: "1px solid #ccc" }}
        title="Doc Editor"
      />
    </div>
  );
}
