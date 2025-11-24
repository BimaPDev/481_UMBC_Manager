import { useState, type FormEvent } from "react";

interface Props {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export default function SearchBar({ onSearch, isLoading }: Props) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSearch(input);
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{ display: "flex", gap: "10px", marginBottom: "20px" }}
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Search Student Name or ID..."
        style={{ flex: 1, padding: "10px" }}
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? "..." : "Search"}
      </button>
    </form>
  );
}
