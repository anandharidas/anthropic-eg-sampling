"use client";
import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [markdown, setMarkdown] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMarkdown(null);
    try {
      const res = await fetch("/api/printable-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
      setMarkdown(data.markdown);
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 800, margin: "40px auto", padding: 16 }}>
      <h1>Printable Summary</h1>
      <p>Enter a PDF or TXT URL. The server will summarize and format it as markdown.</p>
      <form onSubmit={submit} style={{ display: "flex", gap: 8 }}>
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/file.pdf"
          style={{ flex: 1, padding: 8 }}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Processing…" : "Generate"}
        </button>
      </form>

      {error && (
        <pre style={{ color: "crimson", whiteSpace: "pre-wrap", marginTop: 16 }}>{error}</pre>
      )}

      {markdown && (
        <section style={{ marginTop: 24 }}>
          <h2>Markdown Result</h2>
          <pre style={{ whiteSpace: "pre-wrap" }}>{markdown}</pre>
        </section>
      )}
    </main>
  );
}
