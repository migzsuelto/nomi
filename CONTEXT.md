# Nomi

Nomi consolidates bank-export transaction data into a consistent personal-finance record. It preserves the source evidence needed to trace each transaction back to its import.

## Language

**Source file**:
The original CSV or spreadsheet uploaded from a financial institution, retained as evidence for the transactions it contributes.
_Avoid_: Upload, bank file

**Transaction data**:
The persisted, normalized records derived from source files; future UI features may display these records, but that display is outside the initial MVP.
_Avoid_: Import data, spreadsheet rows

**Canonical transaction**:
A normalized transaction-data record with a stable set of fields, independent of the source file's bank-specific column names.
_Avoid_: Spreadsheet row, bank transaction

**Canonical worksheet**:
The single workbook worksheet that contains canonical transactions from every successfully imported source sheet, with enough source details to trace each record back to its evidence.
_Avoid_: Collated sheet, combined bank sheet

**Header mapping**:
A user-confirmed correspondence between a source format's headers and the fields of a canonical transaction.
_Avoid_: Header configuration, column matching

**Format signature**:
The normalized set of a source sheet's headers, used to recognize a reusable header mapping regardless of column order.
_Avoid_: File name, bank name

**Required transaction fields**:
The date, amount, and description fields that every canonical transaction must contain for its source sheet to be eligible for import.
_Avoid_: Minimum columns, required headers

**Source location**:
The filename and worksheet name retained with a canonical transaction to identify the source sheet that produced it.
_Avoid_: Audit metadata, provenance fields

**Duplicate transaction**:
A canonical transaction already persisted from an earlier import, which is skipped rather than stored again.
_Avoid_: Repeated import, copied transaction

**Successful import output**:
The canonical worksheet produced from every source sheet that satisfies the required transaction fields.
_Avoid_: Consolidated file, good-file output

**Failed import output**:
A separate file that reports each selected source file or worksheet that could not be imported and why.
_Avoid_: Error list, rejection report

**Failed imports worksheet**:
The worksheet in a separate failure-report Excel workbook that identifies every failed source file or worksheet and its import failure reason.
_Avoid_: Error spreadsheet, rejection tab

**Fallback mapping agent**:
An AI agent that proposes a header mapping only when deterministic header aliases do not recognize a source format; it receives header names but not transaction values.
_Avoid_: Import agent, AI parser

**Source content hash**:
The hash of an uploaded source file's complete contents, used to recognize an identical file that was already imported.
_Avoid_: Transaction fingerprint, file name

**Saved mapping replacement**:
The confirmed correction that supersedes the saved header mapping for a format signature; transactions already persisted retain the mapping used at their import.
_Avoid_: Mapping merge, retroactive mapping

**Import history**:
The persisted record of prior local imports, retained for future features but not exposed in the MVP user interface.
_Avoid_: Import list, upload history

**Amount transformation**:
The mapping rule that derives the signed canonical amount from either one source amount column or separate debit and credit columns.
_Avoid_: Amount conversion, debit-credit merge

**Date format**:
The user-confirmed interpretation of a source format's date values, saved with its header mapping to resolve otherwise ambiguous numeric dates.
_Avoid_: Locale setting, date guessing

**Manual mapping**:
The user-defined header mapping used when aliases and the fallback mapping agent cannot produce a satisfactory proposal.
_Avoid_: Custom import, hand configuration

**Total import failure**:
An import in which no selected source sheet succeeds; Nomi produces only the failure-report workbook and no empty successful-import workbook.
_Avoid_: Empty consolidation, no-op import

**Local deployment**:
An MVP deployment operated by one person on their own machine, without public multi-user access.
_Avoid_: Public app, shared service

**Canonical worksheet schema**:
The focused set of canonical-transaction fields: date, description, amount, currency, balance, account, reference, source file, and source worksheet. Fields other than date, description, and amount are present when supplied by the source.
_Avoid_: Bank-specific columns, full export schema

**Source currency**:
The currency supplied by a source transaction and retained with its original amount; Nomi does not perform exchange-rate conversion in the MVP.
_Avoid_: Base currency, converted amount

**Known-format import**:
An import whose format signature matches a saved header mapping; the mapping is applied automatically and identified in the import result.
_Avoid_: Reconfirmed mapping, remapped import

**Partial import success**:
An import with at least one successful and one failed source sheet; the result explicitly reports both counts and independently downloads the successful-import and failure-report workbooks.
_Avoid_: Mixed result, incomplete consolidation

**Manual-mapping fallback**:
The path that lets a user complete a new-format import manually when the fallback mapping agent is unavailable or cannot make a usable proposal.
_Avoid_: Agent dependency, blocked import

**Edit mapping action**:
The import-result action that lets a user change a recognized format's saved mapping and confirm its replacement for future imports.
_Avoid_: Automatic remapping, mapping reset

**Canonical transaction order**:
The newest-first ordering of canonical transactions by date, with source file and source worksheet as deterministic tie-breakers.
_Avoid_: Upload order, source order

**Local financial data boundary**:
The rule that source files and transaction values remain on the local machine; the optional fallback mapping agent may receive header names only.
_Avoid_: Cloud processing, remote transaction analysis
