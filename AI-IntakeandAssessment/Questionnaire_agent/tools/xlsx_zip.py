import os
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Tuple

import openpyxl

_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

_coord_re = re.compile(r"^([A-Z]+)(\d+)$")

def _col_letters_to_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n

def _load_shared_strings(z: zipfile.ZipFile) -> List[str]:
    try:
        with z.open("xl/sharedStrings.xml") as f:
            root = ET.fromstring(f.read())
        strings: List[str] = []
        for si in root.findall("a:si", _NS):
            # concat all text nodes in si (handles rich text)
            text_parts = []
            t = si.find("a:t", _NS)
            if t is not None and t.text is not None:
                text_parts.append(t.text)
            else:
                for r in si.findall("a:r", _NS):
                    t2 = r.find("a:t", _NS)
                    if t2 is not None and t2.text is not None:
                        text_parts.append(t2.text)
            strings.append("".join(text_parts))
        return strings
    except KeyError:
        return []

def _first_sheet_path(z: zipfile.ZipFile) -> Tuple[str, str]:
    # Returns (sheet_path, sheet_name)
    with z.open("xl/workbook.xml") as f:
        wb = ET.fromstring(f.read())
    sheets = wb.find("a:sheets", _NS)
    if sheets is None:
        raise ValueError("No sheets found in workbook")
    first = sheets.find("a:sheet", _NS)
    if first is None:
        raise ValueError("Workbook has no visible sheets")
    rid = first.attrib.get(f"{{{_NS['r']}}}id")
    sheet_name = first.attrib.get("name", "Sheet1")

    # map rId -> target
    with z.open("xl/_rels/workbook.xml.rels") as f:
        rels = ET.fromstring(f.read())
    target = None
    for rel in rels.findall("rel:Relationship", _NS):
        if rel.attrib.get("Id") == rid:
            target = rel.attrib.get("Target")
            break
    if not target:
        # fallback to default first worksheet
        target = "worksheets/sheet1.xml"
    # Normalize path
    if not target.startswith("worksheets/"):
        # usually it's relative to xl/
        target = target.lstrip("/")
    sheet_path = f"xl/{target}" if not target.startswith("xl/") else target
    return sheet_path, sheet_name

def _read_sheet_cells(z: zipfile.ZipFile, sheet_path: str, shared: List[str]) -> List[List[str]]:
    with z.open(sheet_path) as f:
        root = ET.fromstring(f.read())
    sheet_data = root.find("a:sheetData", _NS)
    if sheet_data is None:
        return []

    rows: List[List[str]] = []
    for row in sheet_data.findall("a:row", _NS):
        cells = {}
        max_col = 0
        for c in row.findall("a:c", _NS):
            ref = c.attrib.get("r")  # e.g., "C3"
            t = c.attrib.get("t")    # type
            v = c.find("a:v", _NS)
            val = None
            if t == "s":  # shared string
                if v is not None and v.text is not None:
                    idx = int(v.text)
                    val = shared[idx] if 0 <= idx < len(shared) else ""
            elif t == "inlineStr":
                is_el = c.find("a:is", _NS)
                t_el = is_el.find("a:t", _NS) if is_el is not None else None
                val = t_el.text if t_el is not None else ""
            elif t == "b":  # boolean
                val = "TRUE" if (v is not None and v.text == "1") else "FALSE"
            else:
                # number or string result
                val = v.text if v is not None and v.text is not None else ""
            if ref:
                m = _coord_re.match(ref)
                if m:
                    col_idx = _col_letters_to_index(m.group(1))
                    cells[col_idx] = val
                    max_col = max(max_col, col_idx)

        # Flatten into list 1..max_col
        row_vals = ["" for _ in range(max_col)]
        for ci, cv in cells.items():
            # zero-based index
            row_vals[ci - 1] = cv
        rows.append(row_vals)
    return rows

def materialize_clean_xlsx(src_path: str) -> str:
    """
    Read the whole workbook and write a clean .xlsx copy preserving all worksheets.
    Returns the new file path.
    """
    if not zipfile.is_zipfile(src_path):
        raise ValueError(f"{src_path} is not a valid .xlsx (ZIP) file")

    # Use openpyxl to load the full workbook (data_only to get evaluated cell values)
    wb = openpyxl.load_workbook(src_path, data_only=True)

    # Write a clean workbook copy to temp
    tmp = os.path.join(tempfile.gettempdir(), os.path.basename(src_path) + ".clean.xlsx")
    wb.save(tmp)
    return tmp