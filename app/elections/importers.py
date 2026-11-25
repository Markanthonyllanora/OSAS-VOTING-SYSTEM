"""Bulk import of voters from a CSV or Excel (.xlsx) file."""
import csv
import io
import re
from dataclasses import dataclass, field

from django.db import transaction

from .forms import VoterForm
from .models import Candidate

MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB is plenty for a student list
MAX_ROWS = 5000

# Header names we accept for each field (after lowercasing and removing
# spaces / punctuation), so "First Name", "first_name" and "FIRSTNAME" all work.
COLUMN_ALIASES = {
    "voter_id": {"voterid", "id", "studentid", "studentno", "studentnumber", "idnumber", "vcode"},
    "first_name": {"firstname", "first", "givenname"},
    "last_name": {"lastname", "last", "surname", "familyname"},
    "middle_initial": {"middleinitial", "mi", "middlename", "middle"},
    "department": {"department", "dept", "course", "program"},
    "email": {"email", "emailaddress"},
    "status": {"status"},
}
REQUIRED = ["voter_id", "first_name", "last_name", "department", "email"]
FIELD_LABELS = {
    "voter_id": "Voter ID", "first_name": "First Name", "last_name": "Last Name",
    "middle_initial": "M.I.", "department": "Department", "email": "Email",
    "status": "Status",
}

TEMPLATE_HEADER = ["Voter ID", "First Name", "Last Name", "M.I.", "Department", "Email", "Status"]
TEMPLATE_ROWS = [
    ["2026-0001", "Juan", "Dela Cruz", "P", "BSIT", "juan@example.com", "active"],
    ["2026-0002", "Maria", "Santos", "", "BSA", "maria@example.com", "active"],
]


@dataclass
class ImportResult:
    created: int = 0
    skipped: list = field(default_factory=list)  # [(row_number, reason), ...]
    fatal: str = ""                              # whole-file problem


def _normalise_header(text):
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def _cell_to_text(value):
    """Excel hands back numbers as floats (2026001 -> 2026001.0); undo that."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _read_csv(raw):
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not read the file. Please save it as CSV (UTF-8).")

    try:  # Excel in some regions saves CSV with ; or tabs instead of commas
        dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return [[_cell_to_text(c) for c in row] for row in csv.reader(io.StringIO(text), dialect)]


def _read_xlsx(raw):
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise ValueError(
            "Excel (.xlsx) import needs the 'openpyxl' package. "
            "Run: pip install openpyxl  (or upload a .csv file instead)."
        )
    try:
        workbook = load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    except Exception:
        raise ValueError("Could not open the Excel file. Is it a valid .xlsx file?")
    sheet = workbook.active
    return [[_cell_to_text(c) for c in row] for row in sheet.iter_rows(values_only=True)]


def read_rows(upload):
    name = upload.name.lower()
    if upload.size > MAX_UPLOAD_BYTES:
        raise ValueError("File is too large (maximum 2 MB).")
    raw = upload.read()
    if name.endswith(".csv"):
        return _read_csv(raw)
    if name.endswith(".xlsx"):
        return _read_xlsx(raw)
    if name.endswith(".xls"):
        raise ValueError("Old .xls files are not supported. Save it as .xlsx or .csv first.")
    raise ValueError("Please upload a .csv or .xlsx file.")


def _map_columns(header_row):
    """Return {field_name: column_index} or raise if a required column is missing."""
    mapping = {}
    for index, title in enumerate(header_row):
        key = _normalise_header(title)
        for field_name, aliases in COLUMN_ALIASES.items():
            if key in aliases and field_name not in mapping:
                mapping[field_name] = index
    missing = [FIELD_LABELS[f] for f in REQUIRED if f not in mapping]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing) + ".")
    return mapping


def import_voters(upload):
    result = ImportResult()
    try:
        rows = read_rows(upload)
        rows = [r for r in rows if any(c.strip() for c in r)] if rows else []
        if not rows:
            raise ValueError("The file is empty.")
        mapping = _map_columns(rows[0])
    except ValueError as exc:
        result.fatal = str(exc)
        return result

    body = rows[1:]
    if not body:
        result.fatal = "The file has a header but no voters."
        return result
    if len(body) > MAX_ROWS:
        result.fatal = f"Too many rows ({len(body)}). Import at most {MAX_ROWS} at a time."
        return result

    departments = {value.lower(): value for value, _ in Candidate.DEPARTMENT_CHOICES}
    seen_ids, seen_emails = set(), set()

    with transaction.atomic():
        # Row numbers match what the user sees in Excel (header = row 1).
        for offset, row in enumerate(body, start=2):
            def get(name):
                i = mapping.get(name)
                return row[i].strip() if i is not None and i < len(row) else ""

            middle = get("middle_initial")
            data = {
                "voter_id": get("voter_id"),
                "first_name": get("first_name"),
                "last_name": get("last_name"),
                "middle_initial": middle[:1].upper(),  # "Perez" -> "P"
                "department": departments.get(get("department").lower(), get("department")),
                "email": get("email"),
                "status": get("status").lower() or "active",
            }

            form = VoterForm(data)
            if not form.is_valid():
                reason = "; ".join(
                    f"{form.fields[name].label or FIELD_LABELS.get(name, name)}: {errors[0]}"
                    for name, errors in form.errors.items()
                )
                result.skipped.append((offset, reason))
                continue

            voter_id = form.cleaned_data["voter_id"]
            email = form.cleaned_data["email"]
            if voter_id in seen_ids:
                result.skipped.append((offset, f"Voter ID: {voter_id} appears twice in the file."))
                continue
            if email in seen_emails:
                result.skipped.append((offset, f"Email: {email} appears twice in the file."))
                continue

            form.save()
            seen_ids.add(voter_id)
            seen_emails.add(email)
            result.created += 1

    return result