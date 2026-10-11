import assert from "node:assert/strict";
import test from "node:test";

import { supportedFiles } from "./file-selection.js";

test("supportedFiles keeps supported export files regardless of filename casing", () => {
  const files = [
    { name: "checking.CSV" },
    { name: "savings.xlsx" },
    { name: "notes.txt" },
    { name: "archive.xls" },
  ];

  assert.deepEqual(supportedFiles(files).map((file) => file.name), [
    "checking.CSV",
    "savings.xlsx",
    "archive.xls",
  ]);
});
