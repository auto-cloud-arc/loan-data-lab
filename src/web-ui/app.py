from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from pipeline_service import (
    PipelineExecutionError,
    list_sample_inputs,
    prepare_sample_input,
    prepare_uploaded_input,
    run_pipeline,
)


st.set_page_config(page_title="Loan Data Lab", page_icon="🧪", layout="wide")

st.title("Loan Data Lab")
st.caption("Web UI for testing the cleaner and QA validation pipeline end to end.")

with st.sidebar:
    st.header("Input")
    source_mode = st.radio("Choose a dataset", ["Sample data", "Upload CSV"], horizontal=False)

    sample_inputs = list_sample_inputs()
    selected_sample = None
    uploaded_file = None

    if source_mode == "Sample data":
        if not sample_inputs:
            st.error("No sample CSV files were found in sample-data/raw.")
        else:
            selected_sample = st.selectbox(
                "Sample file",
                sample_inputs,
                format_func=lambda path: path.name,
            )
    else:
        uploaded_file = st.file_uploader("Upload raw loan data", type=["csv"])

    override_reconciliation = st.checkbox("Override reconciliation counts")
    source_count = None
    target_count = None
    if override_reconciliation:
        source_count = st.number_input("Source count", min_value=0, value=0, step=1)
        target_count = st.number_input("Target count", min_value=0, value=0, step=1)

    reconciliation_tolerance = st.slider(
        "Reconciliation tolerance",
        min_value=0.0,
        max_value=0.25,
        value=0.01,
        step=0.005,
        format="%.3f",
    )

    run_clicked = st.button("Run pipeline", type="primary", use_container_width=True)

if run_clicked:
    try:
        with st.spinner("Running the cleaner and validator..."):
            if source_mode == "Sample data":
                if selected_sample is None:
                    st.stop()
                input_name, input_path = prepare_sample_input(Path(selected_sample))
                result = run_pipeline(
                    input_name=input_name,
                    input_path=input_path,
                    source_count=int(source_count) if source_count is not None else None,
                    target_count=int(target_count) if target_count is not None else None,
                    reconciliation_tolerance=float(reconciliation_tolerance),
                )
            else:
                if uploaded_file is None:
                    st.warning("Upload a CSV file to continue.")
                    st.stop()
                with TemporaryDirectory(prefix="loan-data-lab-upload-") as upload_dir:
                    input_name, input_path = prepare_uploaded_input(
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        Path(upload_dir),
                    )
                    result = run_pipeline(
                        input_name=input_name,
                        input_path=input_path,
                        source_count=int(source_count) if source_count is not None else None,
                        target_count=int(target_count) if target_count is not None else None,
                        reconciliation_tolerance=float(reconciliation_tolerance),
                    )
            st.session_state["pipeline_result"] = result
            st.session_state.pop("pipeline_error", None)
    except (PipelineExecutionError, ValueError, FileNotFoundError) as exc:
        st.session_state["pipeline_error"] = exc
        st.session_state.pop("pipeline_result", None)

if "pipeline_error" in st.session_state:
    error = st.session_state["pipeline_error"]
    st.error(str(error))
    if isinstance(error, PipelineExecutionError):
        with st.expander("Command output"):
            if error.stdout:
                st.code(error.stdout, language="text")
            if error.stderr:
                st.code(error.stderr, language="text")

result = st.session_state.get("pipeline_result")
if result:
    st.session_state.pop("pipeline_error", None)

    cleaner_col, qa_col, rate_col = st.columns(3)
    cleaner_col.metric("Input records", len(result.input_df))
    qa_col.metric("Cleaned records", result.cleaner_report.get("CleanedRecords", 0))
    rate_col.metric("Cleaner success rate", result.cleaner_report.get("SuccessRate", "0.0%"))

    st.subheader("Input preview")
    st.dataframe(result.input_df, use_container_width=True, hide_index=True)

    st.subheader("Cleaner output")
    cleaner_metrics = st.columns(3)
    cleaner_metrics[0].metric("Exceptions", result.cleaner_report.get("ExceptionRecords", 0))
    cleaner_metrics[1].metric("Total processed", result.cleaner_report.get("TotalRecords", 0))
    cleaner_metrics[2].metric("Generated", result.cleaner_report.get("GeneratedAt", ""))

    exceptions = result.cleaner_report.get("Exceptions", [])
    if exceptions:
        st.dataframe(exceptions, use_container_width=True, hide_index=True)
    else:
        st.success("No cleaner exceptions were reported.")

    st.download_button(
        "Download cleaned CSV",
        data=result.cleaned_csv_bytes,
        file_name=result.cleaned_csv_name,
        mime="text/csv",
    )

    if not result.cleaned_df.empty:
        st.dataframe(result.cleaned_df, use_container_width=True, hide_index=True)
    else:
        st.info("No cleaned records were produced.")

    st.subheader("QA validation")
    if result.qa_skipped_reason:
        st.warning(result.qa_skipped_reason)
    else:
        qa_report = result.qa_report or {}
        reconciliation = qa_report.get("reconciliation", {})
        qa_metrics = st.columns(4)
        qa_metrics[0].metric("Total failures", qa_report.get("total_failures", 0))
        qa_metrics[1].metric("Pass rate", qa_report.get("pass_rate", "0.0%"))
        qa_metrics[2].metric("Validator exit code", result.validator_exit_code or 0)
        qa_metrics[3].metric("Reconciliation", "PASS" if reconciliation.get("passed") else "FAIL")

        failures = qa_report.get("failures", [])
        if failures:
            st.dataframe(failures, use_container_width=True, hide_index=True)
        else:
            st.success("All QA validations passed.")

        if reconciliation:
            st.json(reconciliation)

        st.download_button(
            "Download QA JSON report",
            data=result.qa_report_json_bytes,
            file_name=result.qa_report_json_name or "qa_report.json",
            mime="application/json",
        )
        st.download_button(
            "Download QA Markdown report",
            data=result.qa_report_markdown or "",
            file_name=result.qa_report_markdown_name or "qa_report.md",
            mime="text/markdown",
        )

        with st.expander("Validator command output"):
            if result.validator_stdout:
                st.code(result.validator_stdout, language="text")
            if result.validator_stderr:
                st.code(result.validator_stderr, language="text")
