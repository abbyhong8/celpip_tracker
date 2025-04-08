import os
import requests
import time 
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

API_URL = "https://celpip-registration.paragontesting.ca/registration/api/TestSessions?testPurposeId=1&brandId=1&testTypeId=5&privateOnly=false&regionId=2&sourceRegId="

seen_ids = set()
CUTOFF_DATE = datetime(2025, 5, 1)

# Telegram credentials

def send_notification(location, date, count):
    message = f"📣 {count} seat(s) available at {location} on {date}!"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        print("✅ Sent Telegram message:", response.status_code)
    except Exception as e:
        print("❌ Failed to send message:", e)


def check_for_new_seats():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        for session in data["content"]:
            session_id = session["id"]
            city = session.get("testCentreCity", "").lower()
            seat_count = session.get("warningSeatCount")
            test_date_str = session.get("testDateTimeTestCentre")
            location = session.get("testCentreName")

            if not test_date_str:
                continue

            test_date = datetime.fromisoformat(test_date_str)

            if (
                city == "vancouver"
                and seat_count is not None
                and seat_count > 0
                and test_date < CUTOFF_DATE
                and session_id not in seen_ids
            ):
                send_notification(location, test_date_str, seat_count)
                seen_ids.add(session_id)

    except Exception as e:
        print("⚠️ Error checking seats:", e)

# Main loop
if __name__ == "__main__":
    while True:
        check_for_new_seats()
        time.sleep(300)  # Every 10 minutes
