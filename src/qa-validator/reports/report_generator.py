"""Standalone report generator for QA validation results."""
from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def generate_json_report(
    failures: list[dict],
    total_records: int,
    input_file: str,
    report_dir: str,
) -> str:
    """Generate a JSON QA report from validation failures. Returns the report file path."""
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "input_file": input_file,
        "total_records": total_records,
        "total_failures": len(failures),
        "pass_rate": f"{(1 - len(failures) / max(total_records, 1)) * 100:.1f}%",
        "failures": failures,
    }
    json_path = os.path.join(report_dir, f"qa_report_{timestamp}.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    return json_path


def generate_markdown_report(
    failures: list[dict],
    total_records: int,
    input_file: str,
    report_dir: str,
) -> str:
    """Generate a Markdown QA report from validation failures. Returns the report file path."""
    Path(report_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    pass_rate = f"{(1 - len(failures) / max(total_records, 1)) * 100:.1f}%"

    md_path = os.path.join(report_dir, f"qa_report_{timestamp}.md")
    with open(md_path, "w") as f:
        f.write("# QA Validation Report\n\n")
        f.write(f"**Generated:** {datetime.utcnow().isoformat()}  \n")
        f.write(f"**Input:** {input_file}  \n")
        f.write(f"**Total records:** {total_records}  \n")
        f.write(f"**Total failures:** {len(failures)}  \n")
        f.write(f"**Pass rate:** {pass_rate}  \n\n")
        if failures:
            f.write("## Failures\n\n")
            f.write("| Row | Field | Rule | Value | Message | Severity |\n")
            f.write("|-----|-------|------|-------|---------|----------|\n")
            for fail in failures:
                f.write(
                    f"| {fail.get('row_index')} | {fail.get('field')} | "
                    f"{fail.get('rule_name')} | {fail.get('actual_value')} | "
                    f"{fail.get('message')} | {fail.get('severity')} |\n"
                )
        else:
            f.write("## ✅ All validations passed!\n")
    return md_path
