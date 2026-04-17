from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time
from threading import Thread
from datetime import datetime, timedelta

app = FastAPI()

ESP_IP = "http://10.155.12.11"

schedule = []

class ClassData(BaseModel):
    room: str
    time: str
    duration: int

@app.post("/schedule")
def schedule_class(data: ClassData):

    now = datetime.now()

    start_time = datetime.strptime(data.time, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )

    end_time = start_time + timedelta(minutes=data.duration)

    schedule.append({
        "room": data.room,
        "start": start_time,
        "end": end_time,
        "started": False,
        "ended": False
    })

    return {"status": "Scheduled"}

@app.post("/cancel")
def cancel_class(data: ClassData):

    global schedule

    schedule = [
        item for item in schedule
        if not (item["room"] == data.room and item["start"].strftime("%H:%M") == data.time)
    ]

    return {"status": "Cancelled"}

@app.get("/schedule_list")
def get_schedule():
    return {
        "schedule": [
            {
                "room": s["room"],
                "time": s["start"].strftime("%H:%M"),
                "duration": int((s["end"] - s["start"]).total_seconds() / 60)
            }
            for s in schedule
        ]
    }

def scheduler():
    while True:
        now = datetime.now()

        for item in schedule:

            # -------- TURN ON -------- #
            if not item["started"] and now >= item["start"]:
                print("ON:", item["room"])

                try:
                    requests.get(f"{ESP_IP}/trigger", params={"room": item["room"]}, timeout=2)
                    time.sleep(0.2)   # 🔥 IMPORTANT FIX
                except Exception as e:
                    print("Error:", e)

                item["started"] = True

            # -------- TURN OFF -------- #
            if not item["ended"] and now >= item["end"]:
                print("OFF:", item["room"])

                try:
                    requests.get(f"{ESP_IP}/trigger", params={"room": f"{item['room']}_OFF"}, timeout=2)
                    time.sleep(0.2)   # 🔥 IMPORTANT FIX
                except Exception as e:
                    print("Error:", e)

                item["ended"] = True

        time.sleep(1)

Thread(target=scheduler).start()