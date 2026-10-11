"use client";
import { ChangeEvent, DragEvent, useState } from "react";
import { supportedFiles } from "./file-selection";
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export default function Home() {
  const [files, setFiles] = useState<File[]>([]), [status, setStatus] = useState(""), [isDragging, setIsDragging] = useState(false);
  function setSelectedFiles(newFiles: Iterable<File> | ArrayLike<File>) {
    const acceptedFiles = supportedFiles(newFiles);
    setFiles(acceptedFiles);
    setStatus(acceptedFiles.length ? "" : "Choose CSV, XLSX, or XLS files to continue.");
  }
  function selectFiles(event: ChangeEvent<HTMLInputElement>) { setSelectedFiles(event.target.files ?? []); }
  function dragOver(event: DragEvent<HTMLLabelElement>) { event.preventDefault(); event.dataTransfer.dropEffect = "copy"; setIsDragging(true); }
  function dragLeave(event: DragEvent<HTMLLabelElement>) { if (!event.currentTarget.contains(event.relatedTarget as Node)) setIsDragging(false); }
  function dropFiles(event: DragEvent<HTMLLabelElement>) { event.preventDefault(); setIsDragging(false); setSelectedFiles(event.dataTransfer.files); }
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
    <section className="upload-card"><label className={`dropzone${isDragging ? " dropzone--active" : ""}`} onDragOver={dragOver} onDragLeave={dragLeave} onDrop={dropFiles}><input type="file" multiple accept=".csv,.xlsx,.xls" onChange={selectFiles} /><strong>Drop your files here, or choose files</strong><span>CSV, XLSX, or XLS</span></label>
      {files.length > 0 && <ul>{files.map((file) => <li key={`${file.name}-${file.size}`}>{file.name}</li>)}</ul>}
      <button type="button" disabled={!files.length} onClick={consolidate}>Create my workbook</button>{status && <p className="status" role="status">{status}</p>}
    </section><p className="note">Your source files stay untouched. The download includes the original source filename for every transaction.</p>
  </main>;
}
