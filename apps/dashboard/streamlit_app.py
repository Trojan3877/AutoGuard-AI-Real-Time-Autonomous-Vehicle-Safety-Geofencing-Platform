import os

import streamlit as st
import requests

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.title("🚗 AutoGuard AI Control Center")

if st.button("Check System Health"):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        st.success("API is healthy")
        st.json(response.json())
    except requests.RequestException as exc:
        st.error(f"Could not reach API at {API_BASE_URL}: {exc}")
