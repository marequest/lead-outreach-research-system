#!/usr/bin/env python3
"""
Sanitize Make.com blueprint exports for safe public sharing.

Replaces client-specific identifiers with placeholders while preserving
the full workflow architecture, logic, and prompts.

Connection references (__IMTCONN__) and dynamic mapper expressions
(`{{N.field}}`) are intentionally left intact — they contain no secrets
and are needed to understand the data flow.

Usage:
    python sanitize_blueprints.py <input_dir> <output_dir>
"""
import json
import re
import sys
from pathlib import Path

# Map of literal strings → placeholders. Order matters for some.
REPLACEMENTS = {
    # Google Sheet that holds research + lead state
    "1HcqWNLy5AWudYxtk_OFAw5-1SnNvO76QIX2IXjSlkts": "YOUR_RESEARCH_SHEET_ID",
    # Google Doc that holds the email template / brand voice guide
    "1PDUZQlD-ySc8FWiAANoMSii3yugMK5y7SCXgMMrqT0g": "YOUR_EMAIL_TEMPLATES_DOC_ID",
    # Slack channel that receives drafts and approval prompts
    "C0AC84F3HD1": "YOUR_SLACK_CHANNEL_ID",
    # Operator's work email (kept in some sheet rows / notifications)
    "marko@8figureagency.co": "your-email@example.com",
    # Real lead names/sites baked into OpenAI few-shot example prompts
    "Asma Sheikh":          "Jane Doe",
    "asmasheikh@gmail.co":  "jane.doe@example.com",   # truncated in source
    "Cookware Ninja":       "Example Blog",
    "cookwareninja.com":    "exampleblog.com",
    "Michelle Goldman":     "John Smith",
    "Uchify":               "Sample Blog",
    "uchify.com":           "sampleblog.com",
}


def sanitize_text(text: str) -> tuple[str, dict]:
    """Apply all replacements, return new text + count per replacement."""
    counts = {}
    for old, new in REPLACEMENTS.items():
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            counts[old] = count
    return text, counts


def sanitize_file(in_path: Path, out_path: Path) -> dict:
    """Sanitize one blueprint JSON file."""
    text = in_path.read_text(encoding="utf-8")
    new_text, counts = sanitize_text(text)
    # Validate JSON is still valid after replacement
    json.loads(new_text)
    out_path.write_text(new_text, encoding="utf-8")
    return counts


def main():
    if len(sys.argv) != 3:
        print("Usage: sanitize_blueprints.py <input_dir> <output_dir>")
        sys.exit(1)

    in_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    total_replacements = {}
    for in_file in sorted(in_dir.glob("*.json")):
        out_file = out_dir / in_file.name
        counts = sanitize_file(in_file, out_file)
        print(f"✓ {in_file.name}")
        for k, v in counts.items():
            print(f"    {k[:50]:50s} → {REPLACEMENTS[k]:35s} ({v}x)")
            total_replacements[k] = total_replacements.get(k, 0) + v

    print("\n=== Total replacements ===")
    for k, v in total_replacements.items():
        print(f"  {k[:50]:50s}: {v}")


if __name__ == "__main__":
    main()
