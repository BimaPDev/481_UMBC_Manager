import { type DriveFile } from "../types";

interface Props {
  results: DriveFile[];
  onSelect: (file: DriveFile) => void;
}

export default function ResultList({ results, onSelect }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
      {results.map((file) => (
        <div
          key={file.id}
          onClick={() => onSelect(file)}
          style={{
            border: "1px solid #ddd",
            padding: "10px",
            cursor: "pointer",
            borderRadius: "5px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <strong>{file.name}</strong>
          <div style={{ fontSize: "0.8rem", color: "#666" }}>
            Created: {new Date(file.createdTime).toLocaleDateString()}
          </div>
        </div>
      ))}
    </div>
  );
}
