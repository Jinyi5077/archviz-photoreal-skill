#!/usr/bin/env python3
"""Pair render images with passes. Read-only metadata, not semantic recognition."""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".exr"}
PASS_PATTERN = re.compile(
    r"^(?P<view>.+)_(?P<pass>AI_Albedo|AI_Normal|AI_Material|MaterialID|SkyMask|"
    r"ZDepth|Reflection|Transparent|AO)$", re.IGNORECASE
)
CANONICAL_PASSES = {p.casefold(): p for p in (
    "AI_Albedo", "AI_Normal", "AI_Material", "MaterialID", "SkyMask",
    "ZDepth", "Reflection", "Transparent", "AO"
)}


def natural_key(value):
    return [int(part) if part.isdigit() else part.casefold()
            for part in re.split(r"(\d+)", value)]


def dimensions(path):
    """Read dimensions from PNG/JPEG headers; no image conversion or modification."""
    with path.open("rb") as stream:
        header = stream.read(24)
        if header[:8] == b"\x89PNG\r\n\x1a\n" and header[12:16] == b"IHDR":
            width, height = struct.unpack(">II", header[16:24])
            if width < 1 or height < 1:
                raise ValueError("Invalid PNG dimensions")
            return [width, height]
        if header[:2] != b"\xff\xd8":
            return None
        stream.seek(2)
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while True:
            byte = stream.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            while byte == b"\xff":
                byte = stream.read(1)
            if not byte or byte[0] in {0xD9, 0xDA}:
                return None
            marker = byte[0]
            if marker in {0x01, 0xD8} or 0xD0 <= marker <= 0xD7:
                continue
            size_bytes = stream.read(2)
            if len(size_bytes) != 2:
                return None
            length = struct.unpack(">H", size_bytes)[0]
            if length < 2:
                raise ValueError("Invalid JPEG segment")
            if marker in sof:
                data = stream.read(5)
                if len(data) != 5:
                    return None
                height, width = struct.unpack(">HH", data[1:5])
                return [width, height] if width and height else None
            stream.seek(length - 2, 1)


def file_record(path, root):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    record = {"file": path.relative_to(root).as_posix(), "bytes": path.stat().st_size,
              "sha256": digest.hexdigest(), "dimensions": None}
    try:
        record["dimensions"] = dimensions(path)
    except (OSError, ValueError, struct.error) as error:
        record["metadata_error"] = str(error)
    return record


def inventory(root, include=None):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Input must be a directory")
    selected = {name.casefold() for name in include} if include else None
    groups, unclassified = {}, []
    for path in sorted(root.iterdir(), key=lambda p: natural_key(p.name)):
        if not path.is_file() or path.suffix.casefold() not in IMAGE_EXTENSIONS:
            continue
        match = PASS_PATTERN.match(path.stem)
        if match:
            view, role = match["view"], CANONICAL_PASSES[match["pass"].casefold()]
        elif "_ai_" in path.stem.casefold():
            unclassified.append(path.name)
            continue
        else:
            view, role = path.stem, "beauty"
        if selected is not None and view.casefold() not in selected:
            continue
        group = groups.setdefault(view.casefold(), {"view": view, "files": {}})
        group["files"].setdefault(role, []).append(file_record(path, root))
    views = []
    for group in groups.values():
        files, issues = group["files"], []
        beauty = files.get("beauty", [])
        if not beauty:
            issues.append("orphan_passes_no_beauty")
        for role, records in files.items():
            if len(records) > 1:
                issues.append("duplicate_role:" + role)
            for record in records:
                if not record["dimensions"]:
                    issues.append("dimensions_unverified:" + record["file"])
        if len(beauty) == 1 and beauty[0]["dimensions"]:
            for role, records in files.items():
                if role == "beauty":
                    continue
                for record in records:
                    if record["dimensions"] and record["dimensions"] != beauty[0]["dimensions"]:
                        issues.append("dimension_mismatch:" + record["file"])
        views.append({**group,
                      "missing_ai_passes": [p for p in ("AI_Albedo", "AI_Normal", "AI_Material") if p not in files],
                      "issues": issues, "visual_inspection": "required_not_performed"})
    found = {view["view"].casefold() for view in views}
    return {"schema_version": 1, "source_directory": str(root),
            "scope": "immediate_directory_only", "view_count": len(views),
            "views": views, "unclassified_ai_files": unclassified,
            "requested_views_not_found": sorted(selected - found) if selected else [],
            "note": "Metadata pairing only. Visually inspect every selected beauty and its passes; no identity, geometry, or material recognition has been performed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--include", action="append", help="Exact view stem; repeat to select views")
    parser.add_argument("--out", type=Path, help="New JSON file, never overwrite an existing file")
    args = parser.parse_args()
    result = inventory(args.directory, args.include)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(text)
        print(f"Wrote {result['view_count']} views to {args.out}")
    else:
        print(text)
    return 2 if (result["requested_views_not_found"] or
                 any(view["issues"] for view in result["views"])) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
