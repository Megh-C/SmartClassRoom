import streamlit as st
import requests
import re

BASE_URL = "http://10.155.12.33:3000"

st.title("Class Scheduler")

# -------- INPUT SECTION -------- #
room = st.selectbox("Select Room", ["SJT-401", "SJT-402"])

# NEW: Manual time input
time_input = st.text_input("Enter Time (HH:MM, 24-hour format)", placeholder="14:30")

duration = st.number_input("Duration (minutes)", min_value=1, max_value=180)

# -------- TIME VALIDATION -------- #
def is_valid_time(t):
    return re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", t)

col1, col2 = st.columns(2)

# -------- SCHEDULE BUTTON -------- #
with col1:
    if st.button("Schedule Class"):
        if is_valid_time(time_input):
            requests.post(
                f"{BASE_URL}/schedule",
                json={
                    "room": room,
                    "time": time_input,
                    "duration": duration
                }
            )
            st.success(f"Scheduled {room} at {time_input}")
        else:
            st.error("Invalid time format! Use HH:MM (24-hour)")

# -------- CANCEL BUTTON -------- #
with col2:
    if st.button("Cancel Class"):
        if is_valid_time(time_input):
            requests.post(
                f"{BASE_URL}/cancel",
                json={
                    "room": room,
                    "time": time_input,
                    "duration": duration
                }
            )
            st.warning(f"Cancelled {room} at {time_input}")
        else:
            st.error("Invalid time format! Use HH:MM")

# -------- SHOW SCHEDULE -------- #
st.subheader("Current Schedule")

try:
    res = requests.get(f"{BASE_URL}/schedule_list")
    data = res.json()

    if len(data["schedule"]) == 0:
        st.info("No classes scheduled")

    else:
        for item in data["schedule"]:
            st.write(
                f"Room: {item['room']} | Time: {item['time']} | Duration: {item['duration']} min"
            )

except Exception as e:
    st.error(f"Error: {e}")