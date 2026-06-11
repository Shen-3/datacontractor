import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="DataContractor Dashboard", layout="wide")

st.title("DataContractor Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(["Contracts", "Validation Runs", "Violations", "Demo"])

with tab1:
    st.header("Contracts")
    try:
        resp = requests.get(f"{API_BASE}/contracts", timeout=5)
        if resp.status_code == 200:
            contracts = resp.json()
            if contracts:
                for c in contracts:
                    with st.expander(f"**{c['name']}** - {c['status']} (owner: {c['owner']})"):
                        st.write(f"**Description:** {c.get('description', 'N/A')}")
                        st.write(f"**Created:** {c['created_at']}")

                        versions_resp = requests.get(f"{API_BASE}/contracts/{c['name']}/versions", timeout=5)
                        if versions_resp.status_code == 200:
                            versions = versions_resp.json()
                            if versions:
                                st.subheader("Versions")
                                for v in versions:
                                    active = " (ACTIVE)" if v["is_active"] else ""
                                    st.write(f"- Version {v['version']}{active} - created {v['created_at']}")
                            else:
                                st.info("No versions found")
            else:
                st.info("No contracts found. Run `make seed` to create demo data.")
        else:
            st.error(f"API error: {resp.status_code}")
    except requests.ConnectionError:
        st.error("Cannot connect to API. Make sure the server is running (make api)")

with tab2:
    st.header("Validation Runs")
    try:
        resp = requests.get(f"{API_BASE}/etl/runs", timeout=5)
        if resp.status_code == 200:
            runs = resp.json()
            if runs:
                df = pd.DataFrame(runs)
                st.dataframe(
                    df[["id", "dataset_name", "status", "rows_checked", "violations_count", "started_at"]],
                    use_container_width=True,
                )
            else:
                st.info("No validation runs found. Run a demo scenario first.")
        else:
            st.error(f"API error: {resp.status_code}")
    except requests.ConnectionError:
        st.error("Cannot connect to API.")

with tab3:
    st.header("Violations")
    try:
        resp = requests.get(f"{API_BASE}/violations", timeout=5)
        if resp.status_code == 200:
            violations = resp.json()
            if violations:
                df = pd.DataFrame(violations)
                severity_counts = df["severity"].value_counts()
                st.subheader("Violations by Severity")
                st.bar_chart(severity_counts)

                st.subheader("All Violations")
                st.dataframe(
                    df[["contract_name", "check_name", "severity", "status", "failed_rows_count", "message"]],
                    use_container_width=True,
                )
            else:
                st.info("No violations found.")
        else:
            st.error(f"API error: {resp.status_code}")
    except requests.ConnectionError:
        st.error("Cannot connect to API.")

with tab4:
    st.header("Demo Scenarios")
    st.write("Run demo scenarios using the commands below:")

    demos = [
        ("Valid Dataset", "make demo-valid", "All checks should pass"),
        ("Invalid Enum", "make demo-invalid-enum", "allowed_values check should fail"),
        ("Missing Field", "make demo-invalid-schema", "Schema validation should fail"),
        ("Null Values", "make demo-nulls", "not_null check should fail"),
        ("Duplicates", "make demo-duplicates", "unique check should fail"),
        ("Stale Data", "make demo-stale", "freshness check should fail"),
    ]

    for name, cmd, expected in demos:
        with st.expander(name):
            st.code(cmd, language="bash")
            st.write(f"**Expected:** {expected}")

    st.subheader("Quick Commands")
    st.code("""
# Start API
make api

# Start Dashboard
make dashboard

# Seed demo data
make seed

# Run demo
make demo-valid
    """, language="bash")
