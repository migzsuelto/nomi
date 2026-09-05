"use client";
import { ChangeEvent, useState } from "react";
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export default function Home() {
  const [files, setFiles] = useState<File[]>([]), [status, setStatus] = useState("");
  function selectFiles(event: ChangeEvent<HTMLInputElement>) { setFiles(Array.from(event.target.files ?? [])); setStatus(""); }
  async function consolidate() {
    if (!files.length) return;
    setStatus("Bringing your transactions together…");
    const formData = new FormData(); files.forEach((file) => formData.append("files", file));
    const response = await fetch(`${apiUrl}/api/consolidate`, { method: "POST", body: formData });
    if (!response.ok) { const error = await response.json().catch(() => ({ detail: "Something went wrong." })); setStatus(error.detail ?? "Something went wrong."); return; }
    const link = document.createElement("a"); link.href = URL.createObjectURL(await response.blob()); link.download = "nomi-consolidated-transactions.xlsx"; link.click(); URL.revokeObjectURL(link.href); setStatus("Your consolidated workbook is ready.");
  }
  return <main>
    <p className="eyebrow">Nomi</p><h1>Your money,<br />all in one place.</h1>
    <p className="intro">Add exports from your accounts. Nomi will turn them into one clean Excel workbook.</p>
    <section className="upload-card"><label className="dropzone"><input type="file" multiple accept=".csv,.xlsx,.xls" onChange={selectFiles} /><strong>Choose your files</strong><span>CSV, XLSX, or XLS</span></label>
      {files.length > 0 && <ul>{files.map((file) => <li key={`${file.name}-${file.size}`}>{file.name}</li>)}</ul>}
      <button type="button" disabled={!files.length} onClick={consolidate}>Create my workbook</button>{status && <p className="status" role="status">{status}</p>}
    </section><p className="note">Your source files stay untouched. The download includes the original source filename for every transaction.</p>
  </main>;
}
