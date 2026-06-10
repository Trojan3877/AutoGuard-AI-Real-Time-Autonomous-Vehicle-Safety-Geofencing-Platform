import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

# App Configuration
st.set_page_config(page_title="AutoGuard-AI Telemetry", page_icon="🚗", layout="wide")

st.title("🚗 AutoGuard-AI: Autonomous Vehicle Safety Geofencing Platform")
st.caption("Edge Compute Simulation Stack | Real-Time Spatial Boundary Interception & Collision Avoidance")

# --- SIDEBAR: VEHICLE NAVIGATION CONTROL ---
st.sidebar.header("🕹️ Vehicle Telemetry Controller")
st.sidebar.markdown("Manipulate vehicle telemetry and dynamic hazards to test AutoGuard-AI's spatial compliance loops.")

# Operational parameters
velocity = st.sidebar.slider("Vehicle Velocity (mph)", 0, 80, 35)
refresh_rate = st.sidebar.slider("Sensor Ingestion Interval (ms)", 10, 500, 100)
active_geofence = st.sidebar.selectbox("Geofence Boundary Mode", ["Strict Urban Core", "Highway Construction Corridor", "Custom Proximity Buffer"])

st.sidebar.markdown("---")
st.sidebar.subheader("⚠️ Hazard Injection Matrix")
inject_breach = st.sidebar.button("🚨 Force Immediate Perimeter Breach")
inject_sensor_fault = st.sidebar.toggle("❌ Simulate LiDAR / GPS Drop")

# Session state initialization for historical logs
if "telemetry_logs" not in st.session_state:
    st.session_state.telemetry_logs = []
if "vehicle_pos" not in st.session_state:
    st.session_state.vehicle_pos = {"x": 0.0, "y": 0.0}

# Update position dynamically to simulate movement trajectory
if not inject_breach:
    st.session_state.vehicle_pos["x"] += (velocity * 0.01) + np.random.uniform(-0.05, 0.05)
    st.session_state.vehicle_pos["y"] += np.random.uniform(-0.1, 0.1)
else:
    # Snap position completely outside standard bounds
    st.session_state.vehicle_pos["x"] = 7.5
    st.session_state.vehicle_pos["y"] = 6.8

# --- CORE SPATIAL COMPLIANCE ENGINE ---
def evaluate_geofence_compliance(pos, hazard_fault):
    """
    Simulates spatial grid checking loops. In production, this maps to optimized
    CUDA kernels evaluating polygon vertex constraints under sub-millisecond conditions.
    """
    if hazard_fault:
        return "SENS_ERR", 100.0, "CRITICAL: Sensor Degraded. Defaulting to safe emergency deceleration."
        
    # Define an arbitrary boundary radius of 6.5 units from root origin
    distance_from_center = np.sqrt(pos["x"]**2 + pos["y"]**2)
    
    if distance_from_center >= 6.5:
        return "VIOLATION", distance_from_center, "🚨 BREACH DETECTED: Activating Drive-by-Wire override. Hard braking deployed."
    elif distance_from_center >= 4.5:
        return "WARNING", distance_from_center, "⚠️ PROXIMITY ALERT: Vehicle approaching perimeter boundary buffer."
    return "SAFE", distance_from_center, "Perimeter Clear. Autonomous trajectory optimization active."

# Execute current frame verification
status, distance, mitigation = evaluate_geofence_compliance(st.session_state.vehicle_pos, inject_sensor_fault)

# Track logs
frame_payload = {
    "Timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
    "Coordinates": f"({st.session_state.vehicle_pos['x']:.2f}, {st.session_state.vehicle_pos['y']:.2f})",
    "Boundary Distance (m)": round(distance, 3),
    "System State": status,
    "Safety Directive": mitigation
}
st.session_state.telemetry_logs.insert(0, frame_payload)
if len(st.session_state.telemetry_logs) > 50:
    st.session_state.telemetry_logs.pop()

# --- MAIN DASHBOARD VISUALIZATIONS ---
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    if status == "SAFE":
        st.success("🟢 CORE STATUS: NOMINAL")
    elif status == "WARNING":
        st.warning("🟡 CORE STATUS: BUFFER WARNING")
    else:
        st.error("🔴 CORE STATUS: SAFETY OVERRIDE")
with col_m2:
    st.metric("Spatial Edge Compute Latency", f"{np.random.uniform(0.18, 0.42):.3f} ms", delta="CUDA Accelerated")
with col_m3:
    st.metric("Ingested Coordinate Delta (Δ)", f"{distance:.2f}m to Edge")

col_left, col_right = st.columns([4, 3])

with col_left:
    st.subheader("🗺️ Real-Time Spatial Telemetry Vector Map")
    
    # Generate 2D spatial plotting environment via Matplotlib
    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_facecolor('#0e1117') # Match Streamlit Default Dark Background
    ax.set_facecolor('#1f242d')
    
    # Draw circular geofence boundary rings
    circle_safe = plt.Circle((0, 0), 4.5, color='yellow', fill=False, linestyle='--', alpha=0.4, label='Warning Buffer')
    circle_danger = plt.Circle((0, 0), 6.5, color='red', fill=False, linestyle='-', linewidth=2, label='Geofence Boundary')
    ax.add_patch(circle_safe)
    ax.add_patch(circle_danger)
    
    # Plot historical trajectory tail points if available
    if len(st.session_state.telemetry_logs) > 1:
        hist_x = [float(log["Coordinates"].split(",")[0].replace("(", "")) for log in st.session_state.telemetry_logs[::-1]]
        hist_y = [float(log["Coordinates"].split(",")[1].replace(")", "")) for log in st.session_state.telemetry_logs[::-1]]
        ax.plot(hist_x, hist_y, color='#00f2fe', alpha=0.4, linestyle=':', label='Trajectory Tail')
        
    # Plot active vehicle asset coordinates
    v_color = '#ff4b4b' if status in ["VIOLATION", "SENS_ERR"] else ('#ffa500' if status == "WARNING" else '#00ff00')
    ax.scatter(st.session_state.vehicle_pos["x"], st.session_state.vehicle_pos["y"], color=v_color, s=150, zorder=5, label='AV Asset')
    
    # Graphic grid tunings
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.grid(True, color='#2d323f', linestyle='-', alpha=0.5)
    ax.tick_params(colors='white')
    ax.set_xlabel("X-Coordinate (Meters)", color='white')
    ax.set_ylabel("Y-Coordinate (Meters)", color='white')
    ax.legend(facecolor='#1f242d', labelcolor='white', loc='upper right')
    
    st.pyplot(fig)

with col_right:
    st.subheader("📋 Drive-By-Wire Event Ledger")
    if st.session_state.telemetry_logs:
        df_logs = pd.DataFrame(st.session_state.telemetry_logs)
        
        def highlight_states(val):
            if val == "VIOLATION" or val == "SENS_ERR": return "background-color: rgba(255, 75, 75, 0.25); color: #ff4b4b; font-weight: bold;"
            if val == "WARNING": return "background-color: rgba(255, 165, 0, 0.2); color: #ffa500;"
            return "background-color: rgba(0, 255, 0, 0.05); color: #00ff00;"

        st.dataframe(df_logs.style.map(highlight_states, subset=["System State"]), use_container_width=True, hide_index=True)

# Polling frequency loop timing
time.sleep(refresh_rate / 1000.0)
st.rerun()