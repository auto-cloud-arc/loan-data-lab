from __future__ import annotations

from io import BytesIO
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
CLEANER_PROJECT = REPO_ROOT / "src/data-cleaner-csharp/ContosoLoanCleaner/ContosoLoanCleaner.csproj"
VALIDATOR_SCRIPT = REPO_ROOT / "src/qa-validator/runners/run_validations.py"
SAMPLE_DATA_DIR = REPO_ROOT / "sample-data/raw"
REQUIRED_COLUMNS = {
    "ApplicationId",
    "CustomerId",
    "BranchCode",
    "LoanAmount",
    "LoanType",
    "ApplicationDate",
    "FirstName",
    "LastName",
    "Ssn",
    "PhoneNumber",
    "AddressLine1",
    "City",
    "StateCode",
    "ZipCode",
    "Email",
    "CollateralValue",
}
VALIDATOR_COLUMN_MAP = {
    "ApplicationId": "application_id",
    "CustomerId": "customer_id",
    "BranchCode": "branch_code",
    "LoanAmount": "loan_amount",
    "LoanType": "loan_type",
    "ApplicationDate": "application_date",
    "FirstName": "first_name",
    "LastName": "last_name",
    "Ssn": "ssn",
    "PhoneNumber": "phone_number",
    "AddressLine1": "address_line_1",
    "City": "city",
    "StateCode": "state_code",
    "ZipCode": "zip_code",
    "Email": "email",
    "CollateralValue": "collateral_value",
}


class PipelineExecutionError(RuntimeError):
    def __init__(self, step: str, message: str, *, stdout: str = "", stderr: str = "") -> None:
        super().__init__(message)
        self.step = step
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class PipelineArtifacts:
    input_name: str
    input_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    cleaned_csv_name: str
    cleaned_csv_bytes: bytes
    cleaner_report: dict[str, Any]
    qa_report: dict[str, Any] | None
    qa_report_json_name: str | None
    qa_report_json_bytes: bytes | None
    qa_report_markdown_name: str | None
    qa_report_markdown: str | None
    qa_skipped_reason: str | None
    cleaner_stdout: str
    cleaner_stderr: str
    validator_stdout: str
    validator_stderr: str
    validator_exit_code: int | None


def list_sample_inputs() -> list[Path]:
    return sorted(
        path
        for path in SAMPLE_DATA_DIR.glob("*.csv")
        if REQUIRED_COLUMNS.issubset(set(pd.read_csv(path, nrows=0).columns))
    )


def sanitize_file_name(file_name: str) -> str:
    candidate = Path(file_name).name.strip() or "loan_data.csv"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(candidate).stem).strip("._") or "loan_data"
    suffix = Path(candidate).suffix.lower() or ".csv"
    if suffix != ".csv":
        raise ValueError("Only CSV files are supported.")
    return f"{stem}{suffix}"


def dataframe_from_csv_bytes(csv_bytes: bytes) -> pd.DataFrame:
    if not csv_bytes.strip():
        return pd.DataFrame()
    return pd.read_csv(BytesIO(csv_bytes))


def latest_report_path(report_dir: Path, suffix: str) -> Path:
    matches = sorted(report_dir.glob(f"*.{suffix}"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not matches:
        raise FileNotFoundError(f"No .{suffix} report was generated in {report_dir}.")
    return matches[0]


def prepare_uploaded_input(file_name: str, content: bytes, workspace_dir: Path) -> tuple[str, Path]:
    safe_name = sanitize_file_name(file_name)
    input_path = workspace_dir / safe_name
    input_path.write_bytes(content)
    return safe_name, input_path


def prepare_sample_input(sample_path: Path) -> tuple[str, Path]:
    resolved_sample = sample_path.resolve()
    sample_root = SAMPLE_DATA_DIR.resolve()
    if sample_root not in resolved_sample.parents:
        raise ValueError("Sample input must come from sample-data/raw.")
    return resolved_sample.name, resolved_sample


def validate_input_dataframe(input_df: pd.DataFrame) -> None:
    missing_columns = sorted(REQUIRED_COLUMNS.difference(input_df.columns))
    if missing_columns:
        raise ValueError(f"Input CSV is missing required columns: {', '.join(missing_columns)}")


def prepare_validator_input(cleaned_df: pd.DataFrame, validator_input_path: Path) -> None:
    cleaned_df.rename(columns=VALIDATOR_COLUMN_MAP).to_csv(validator_input_path, index=False)


def run_pipeline(
    *,
    input_name: str,
    input_path: Path,
    source_count: int | None = None,
    target_count: int | None = None,
    reconciliation_tolerance: float = 0.01,
) -> PipelineArtifacts:
    input_bytes = input_path.read_bytes()
    input_df = dataframe_from_csv_bytes(input_bytes)
    validate_input_dataframe(input_df)

    with TemporaryDirectory(prefix="loan-data-lab-ui-") as temp_dir:
        workspace_dir = Path(temp_dir)
        cleaned_csv_name = f"{Path(input_name).stem}_cleaned.csv"
        cleaned_csv_path = workspace_dir / cleaned_csv_name
        exception_report_path = workspace_dir / f"{Path(input_name).stem}_exceptions.json"

        cleaner_result = subprocess.run(
            [
                "dotnet",
                "run",
                "--project",
                str(CLEANER_PROJECT),
                "--",
                str(input_path),
                str(cleaned_csv_path),
                str(exception_report_path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if cleaner_result.returncode != 0:
            raise PipelineExecutionError(
                "cleaner",
                "The C# data cleaner failed.",
                stdout=cleaner_result.stdout,
                stderr=cleaner_result.stderr,
            )

        if not exception_report_path.exists():
            raise PipelineExecutionError(
                "cleaner",
                "The cleaner finished without writing its exception report.",
                stdout=cleaner_result.stdout,
                stderr=cleaner_result.stderr,
            )

        cleaner_report = json.loads(exception_report_path.read_text(encoding="utf-8"))
        cleaned_csv_bytes = cleaned_csv_path.read_bytes() if cleaned_csv_path.exists() else b""
        cleaned_df = dataframe_from_csv_bytes(cleaned_csv_bytes)

        if cleaner_report.get("CleanedRecords", 0) <= 0 or cleaned_df.empty:
            return PipelineArtifacts(
                input_name=input_name,
                input_df=input_df,
                cleaned_df=cleaned_df,
                cleaned_csv_name=cleaned_csv_name,
                cleaned_csv_bytes=cleaned_csv_bytes,
                cleaner_report=cleaner_report,
                qa_report=None,
                qa_report_json_name=None,
                qa_report_json_bytes=None,
                qa_report_markdown_name=None,
                qa_report_markdown=None,
                qa_skipped_reason="QA validation was skipped because the cleaner produced no valid rows.",
                cleaner_stdout=cleaner_result.stdout,
                cleaner_stderr=cleaner_result.stderr,
                validator_stdout="",
                validator_stderr="",
                validator_exit_code=None,
            )

        qa_report_dir = workspace_dir / "qa-reports"
        validator_input_path = workspace_dir / "validator_input.csv"
        prepare_validator_input(cleaned_df, validator_input_path)
        validator_command = [
            sys.executable,
            str(VALIDATOR_SCRIPT),
            "--input",
            str(validator_input_path),
            "--report-dir",
            str(qa_report_dir),
            "--reconciliation-tolerance",
            str(reconciliation_tolerance),
        ]

        if source_count is not None:
            validator_command.extend(["--source-count", str(source_count)])
        if target_count is not None:
            validator_command.extend(["--target-count", str(target_count)])

        validator_result = subprocess.run(
            validator_command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        if validator_result.returncode not in (0, 1):
            raise PipelineExecutionError(
                "validator",
                "The QA validator failed before producing a report.",
                stdout=validator_result.stdout,
                stderr=validator_result.stderr,
            )

        qa_json_path = latest_report_path(qa_report_dir, "json")
        qa_md_path = latest_report_path(qa_report_dir, "md")
        qa_report_json_bytes = qa_json_path.read_bytes()
        qa_report_markdown = qa_md_path.read_text(encoding="utf-8")

        return PipelineArtifacts(
            input_name=input_name,
            input_df=input_df,
            cleaned_df=cleaned_df,
            cleaned_csv_name=cleaned_csv_name,
            cleaned_csv_bytes=cleaned_csv_bytes,
            cleaner_report=cleaner_report,
            qa_report=json.loads(qa_report_json_bytes.decode("utf-8")),
            qa_report_json_name=qa_json_path.name,
            qa_report_json_bytes=qa_report_json_bytes,
            qa_report_markdown_name=qa_md_path.name,
            qa_report_markdown=qa_report_markdown,
            qa_skipped_reason=None,
            cleaner_stdout=cleaner_result.stdout,
            cleaner_stderr=cleaner_result.stderr,
            validator_stdout=validator_result.stdout,
            validator_stderr=validator_result.stderr,
            validator_exit_code=validator_result.returncode,
        )
