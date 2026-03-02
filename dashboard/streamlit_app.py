import streamlit as st
import requests

st.title("🚗 AutoGuard AI Control Center")

if st.button("Check System Health"):
    response = requests.get("http://localhost:8000/health")
    st.write(response.json())
