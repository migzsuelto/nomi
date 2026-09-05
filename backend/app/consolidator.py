from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

OUTPUT_COLUMNS = ["date", "processed_date", "type", "description", "particulars", "code", "reference", "amount", "balance", "account", "category", "currency", "source_file"]
ALIASES = {
    "date": ("transaction date", "date", "transaction date/time"), "processed_date": ("processed date", "posting date"),
    "type": ("type", "transaction type"), "description": ("details", "description", "merchant", "payee"),
    "particulars": ("particulars",), "code": ("code",), "reference": ("reference", "transaction reference"),
    "amount": ("amount", "transaction amount"), "balance": ("balance", "running balance"),
    "account": ("to/from account number", "account", "account number"), "category": ("category",), "currency": ("currency",),
}

class UnsupportedWorkbook(ValueError):
    pass

def _clean(value: object) -> str:
    return "" if pd.isna(value) else str(value).strip().lower()

def _find_header_row(raw: pd.DataFrame) -> int:
    for index, row in raw.head(25).iterrows():
        values = {_clean(value) for value in row}
        if "amount" in values and ("date" in values or "transaction date" in values):
            return int(index)
    raise UnsupportedWorkbook("Could not find a transaction header row with Date and Amount columns.")

def _read_table(content: bytes, filename: str) -> pd.DataFrame:
    suffix, stream = Path(filename).suffix.lower(), BytesIO(content)
    if suffix == ".csv": return pd.read_csv(stream, header=None)
    if suffix in {".xlsx", ".xls"}: return pd.read_excel(stream, header=None)
    raise UnsupportedWorkbook("Only CSV, XLSX, and XLS files are supported.")

def _map_columns(table: pd.DataFrame, filename: str) -> pd.DataFrame:
    header_row = _find_header_row(table)
    data = table.iloc[header_row + 1:].copy()
    data.columns = [_clean(value) for value in table.iloc[header_row]]
    data = data.dropna(how="all")
    output = pd.DataFrame(index=data.index)
    for destination in OUTPUT_COLUMNS:
        if destination == "source_file": output[destination] = filename; continue
        source = next((name for name in ALIASES.get(destination, ()) if name in data.columns), None)
        output[destination] = data[source] if source else None
    if "details" in data.columns and "code" in data.columns:
        # Some bank Visa rows place a masked card number in Details and the merchant in Code.
        masked_card = data["details"].astype(str).str.contains(r"\d{4}[-*]", regex=True, na=False)
        output.loc[masked_card & data["code"].notna(), "description"] = data.loc[masked_card & data["code"].notna(), "code"]
    if output["amount"].isna().all(): raise UnsupportedWorkbook(f"{filename} has no usable Amount column.")
    output["date"] = pd.to_datetime(output["date"], errors="coerce", dayfirst=True)
    output["processed_date"] = pd.to_datetime(output["processed_date"], errors="coerce", dayfirst=True)
    output["amount"] = pd.to_numeric(output["amount"], errors="coerce")
    for column in ["type", "description", "particulars", "code", "reference", "account", "category", "currency", "source_file"]:
        output[column] = output[column].astype("string")
    header = " ".join(_clean(value) for value in table.iloc[:6].fillna("").to_numpy().flatten())
    if "american express" in header:
        output["amount"] = -output["amount"].abs()
        output["type"] = output["type"].fillna("Card purchase")
    return output.dropna(subset=["date", "amount"]).reset_index(drop=True)

def consolidate(files: list[tuple[str, bytes]]) -> pd.DataFrame:
    if not files: raise UnsupportedWorkbook("Upload at least one file.")
    frames = [_map_columns(_read_table(content, name), name) for name, content in files]
    return pd.concat(frames, ignore_index=True).sort_values("date", ascending=False).reset_index(drop=True)

def as_excel(data: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl", datetime_format="yyyy-mm-dd") as writer:
        data.to_excel(writer, sheet_name="Transactions", index=False)
        sheet = writer.book["Transactions"]
        sheet.freeze_panes, sheet.auto_filter.ref = "A2", sheet.dimensions
        for column in sheet.columns:
            sheet.column_dimensions[column[0].column_letter].width = min(max(len(str(cell.value or "")) for cell in column) + 2, 36)
        for cell in sheet["H"][1:]: cell.number_format = "#,##0.00;[Red]-#,##0.00"
    return output.getvalue()
