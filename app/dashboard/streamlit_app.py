"""DataContractor — Streamlit monitoring dashboard.

Connects to the FastAPI backend to display contracts, validation runs,
and violations.  The backend URL is controlled by the ``API_BASE_URL``
environment variable (defaults to ``http://localhost:8000``).
"""

import os
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="DataContractor Dashboard", layout="wide")
st.title(":bar_chart: DataContractor Dashboard")


def safe_api_get(path: str) -> tuple[list | dict | None, str | None]:
    """Fetch JSON from the API and return ``(data, error)``."""
    try:
        resp = requests.get(f"{API_BASE}{path}", timeout=10)
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, f"API error {resp.status_code}: {resp.text[:200]}"
    except requests.ConnectionError:
        return None, "Cannot connect to API — is the server running?"
    except requests.Timeout:
        return None, "API request timed out."
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


# ---- Sidebar ----
st.sidebar.header("Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh every 30 s", value=False)
if st.sidebar.button("Refresh now"):
    st.rerun()
st.sidebar.caption(f"Last updated: {datetime.now():%H:%M:%S}")
st.sidebar.divider()
st.sidebar.caption(f"API: `{API_BASE}`")

# ---- Main content ----
tab1, tab2, tab3, tab4 = st.tabs(["Contracts", "Validation Runs", "Violations", "Demo"])

# =============================================================================
# Tab 1 — Contracts
# =============================================================================
with tab1:
    st.header("Contracts")
    data, err = safe_api_get("/contracts")
    if err:
        st.error(err)
    elif isinstance(data, list):
        n_active = sum(1 for c in data if c.get("status") == "active")
        col1, col2 = st.columns(2)
        col1.metric("Total contracts", len(data))
        col2.metric("Active", n_active)

        if data:
            for c in data:
                with st.expander(f"**{c['name']}** — _{c['status']}_ (owner: {c['owner']})"):
                    st.write(f"**Description:** {c.get('description', 'N/A')}")
                    st.write(f"**Created:** {c.get('created_at', 'N/A')}")

                    versions_data, ver_err = safe_api_get(f"/contracts/{c['name']}/versions")
                    if ver_err:
                        st.warning(ver_err)
                    elif versions_data:
                        st.subheader("Versions")
                        for v in versions_data:
                            active = " *(ACTIVE)*" if v.get("is_active") else ""
                            st.write(f"- **v{v['version']}**{active} — created {v.get('created_at', '')}")
                    else:
                        st.info("No versions found")
        else:
            st.info("No contracts. Run `make seed` to create demo data.")

# =============================================================================
# Tab 2 — Validation Runs
# =============================================================================
with tab2:
    st.header("Validation Runs")
    data, err = safe_api_get("/etl/runs")
    if err:
        st.error(err)
    elif isinstance(data, list):
        if data:
            df = pd.DataFrame(data)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total runs", len(df))
            if "status" in df.columns:
                status_counts = df["status"].value_counts()
                col2.metric("Passed", int(status_counts.get("passed", 0)))
            if "violations_count" in df.columns:
                col3.metric("Total violations", int(df["violations_count"].sum()))

            display_cols = [
                "id",
                "dataset_name",
                "status",
                "rows_checked",
                "violations_count",
                "started_at",
            ]
            available = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available], use_container_width=True)
        else:
            st.info("No validation runs found. Run a demo scenario first.")

# =============================================================================
# Tab 3 — Violations
# =============================================================================
with tab3:
    st.header("Violations")
    data, err = safe_api_get("/violations")
    if err:
        st.error(err)
    elif isinstance(data, list):
        if data:
            df = pd.DataFrame(data)
            total = len(df)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total", total)
            if "severity" in df.columns:
                for col, sev in zip([col2, col3, col4], ["critical", "error", "warning"]):
                    count = int((df["severity"] == sev).sum())
                    col.metric(sev.capitalize(), count)

            if "severity" in df.columns:
                st.subheader("By Severity")
                severity_counts = df["severity"].value_counts()
                st.bar_chart(severity_counts)

            st.subheader("All Violations")
            display_cols = [
                "contract_name",
                "check_name",
                "severity",
                "status",
                "failed_rows_count",
                "message",
            ]
            available = [c for c in display_cols if c in df.columns]
            st.dataframe(df[available], use_container_width=True)
        else:
            st.info("No violations found.")

# =============================================================================
# Tab 4 — Demo Scenarios
# =============================================================================
with tab4:
    st.header("Demo Scenarios")
    st.write("Run these demo scenarios to test the platform:")

    demos = [
        ("Valid Dataset", "make demo-valid", "All checks should pass"),
        ("Invalid Enum", "make demo-invalid-enum", "`allowed_values` check should fail"),
        ("Missing Field", "make demo-invalid-schema", "Schema validation should fail"),
        ("Null Values", "make demo-nulls", "`not_null` check should fail"),
        ("Duplicates", "make demo-duplicates", "`unique` check should fail"),
        ("Stale Data", "make demo-stale", "`freshness` check should fail"),
    ]
    for name, cmd, expected in demos:
        with st.expander(name):
            st.code(cmd, language="bash")
            st.write(f"**Expected:** {expected}")

    st.subheader("Quick Commands")
    st.code(
        """\
# Start the stack
make api
make dashboard
make seed

# Run scenarios
make demo-valid
make demo-invalid-enum
make demo-stale
""",
        language="bash",
    )

# ---- Auto-refresh ----
if auto_refresh:
    st.rerun()
