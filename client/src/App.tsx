import { useState } from "react";
import axios from "axios";
import SearchBar from "./components/SearchBar";
import ResultList from "./components/ResultList";
import DocWorkspace from "./components/DocWorkspace";
import { type DriveFile } from "./types";
import "./App.css";

function App() {
  const [results, setResults] = useState<DriveFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<DriveFile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError("");
    setSelectedFile(null); // Reset selection on new search
    try {
      const res = await axios.get<DriveFile[]>(
        `http://localhost:8000/search?query=${query}`
      );
      setResults(res.data);
      if (res.data.length === 0) setError("No docs found.");
    } catch (err) {
      setError("Search failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1>🎓 UMBC Plan Manager</h1>

      {/* CONDITIONAL RENDERING: Show Workspace OR Search */}
      {selectedFile ? (
        <DocWorkspace
          file={selectedFile}
          onBack={() => setSelectedFile(null)}
        />
      ) : (
        <>
          <SearchBar onSearch={handleSearch} isLoading={loading} />
          {error && <p style={{ color: "red" }}>{error}</p>}
          <ResultList results={results} onSelect={setSelectedFile} />
        </>
      )}
    </div>
  );
}

export default App;
