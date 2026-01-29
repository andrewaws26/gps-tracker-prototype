import streamlit as st
from streamlit_js_eval import get_geolocation
import pandas as pd
from datetime import datetime
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Poor Richard's Logistics", page_icon="🚛")

# --- SIMULATED DATABASE (Session State) ---
# In production, you would replace this with Google Sheets or SQL
if 'fleet_data' not in st.session_state:
    st.session_state.fleet_data = pd.DataFrame(columns=["Driver", "Status", "Time", "lat", "lon"])

# --- FUNCTIONS ---
def save_location(driver_name, status, loc_data):
    # Safe check: ensure we actually have coordinates before saving
    if loc_data and 'coords' in loc_data:
        lat = loc_data['coords']['latitude']
        lon = loc_data['coords']['longitude']
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        new_entry = {
            "Driver": driver_name, 
            "Status": status, 
            "Time": timestamp, 
            "lat": lat, 
            "lon": lon
        }
        
        # Add to our "Database"
        st.session_state.fleet_data = pd.concat(
            [st.session_state.fleet_data, pd.DataFrame([new_entry])], 
            ignore_index=True
        )
        st.success(f"✅ Logged: {status} at {timestamp}")
    else:
        st.error("Could not save: GPS data missing.")

# --- APP LAYOUT ---
st.title("🚛 Logistics Tracker")

# We use tabs to simulate the two different users
tab_driver, tab_juan = st.tabs(["👤 Driver View", "🗺️ Juan's Dashboard"])

# ------------------------------------------------------------------
# TAB 1: THE DRIVER (Mobile Interface)
# ------------------------------------------------------------------
with tab_driver:
    st.header("Driver Check-In")
    
    # 1. Select Driver (Hardcoded for demo)
    driver_name = st.selectbox("Select Driver", ["Andrew (You)", "Driver 2", "Shuttle"])
    
    # 2. Get GPS Location
    # This runs JavaScript to ask the browser for location
    loc = get_geolocation(component_key="get_loc")

    # 3. Big Action Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🟢 START PICKUP", use_container_width=True):
            if loc and 'coords' in loc:
                save_location(driver_name, "Started Pickup", loc)
            else:
                st.warning("⚠️ Waiting for GPS... (Allow Location)")

    with col2:
        if st.button("🔴 DROPPED OFF", use_container_width=True):
            if loc and 'coords' in loc:
                save_location(driver_name, "Dropped Off", loc)
            else:
                st.warning("⚠️ Waiting for GPS... (Allow Location)")

    # --- CRASH FIX IS HERE ---
    # We check if 'coords' exists inside 'loc' before trying to print it.
    if loc:
        if 'coords' in loc:
            st.caption(f"📍 GPS Locked: {loc['coords']['latitude']}, {loc['coords']['longitude']}")
        else:
            # This handles the browser error gracefully instead of crashing
            st.warning(f"⚠️ GPS Signal: {loc}")

# ------------------------------------------------------------------
# TAB 2: JUAN'S DASHBOARD (The "God Mode")
# ------------------------------------------------------------------
with tab_juan:
    st.header("Live Fleet Map")
    
    # Refresh button to fetch latest data
    if st.button("🔄 Refresh Map"):
        st.rerun()

    # Check if we have data
    if not st.session_state.fleet_data.empty:
        # 1. THE MAP
        st.map(st.session_state.fleet_data)
        
        # 2. THE DATA TABLE
        st.subheader("Activity Log")
        st.dataframe(
            st.session_state.fleet_data.sort_values(by="Time", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Waiting for drivers to check in...")