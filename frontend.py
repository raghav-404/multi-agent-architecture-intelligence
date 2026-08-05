import os

import requests
import streamlit as st
from dotenv import load_dotenv

from utils import make_pdf


load_dotenv()

st.set_page_config(page_title="Architecture Intelligence", layout="wide")
st.title("Architecture Intelligence")
st.caption("Enter a project idea and generate a software engineering report.")

project = st.text_area(
    "Project idea",
    placeholder="Example: Build an Online Food Delivery System",
    height=120,
)

if "report" not in st.session_state:
    st.session_state.report = ""

if st.button("Generate Report", type="primary"):
    if not project.strip():
        st.warning("Please enter a project idea.")
    else:
        api_url = os.getenv("API_URL", "http://127.0.0.1:8000/analyze")
        with st.spinner("Analyzing..."):
            response = requests.post(api_url, json={"project": project}, timeout=120)
            st.session_state.report = response.text

if st.session_state.report:
    report = st.session_state.report
    st.download_button(
        "Download PDF",
        data=make_pdf(report),
        file_name="architecture_report.pdf",
        mime="application/pdf",
    )

    sections = {
        "Requirements": "## Requirements",
        "Project Plan": "## Project Plan",
        "Architecture": "## Architecture",
        "Database": "## Database Design",
        "Review": "# Reviewer Notes",
        "Full Report": "# Architecture Intelligence Report",
    }

    tabs = st.tabs(list(sections.keys()))
    headings = list(sections.values())

    for tab, title, heading in zip(tabs, sections.keys(), headings):
        start = report.find(heading)
        end = min(
            [report.find(h, start + 1) for h in headings if report.find(h, start + 1) != -1]
            or [len(report)]
        )
        with tab:
            st.markdown(report if title == "Full Report" else report[start:end])
