from googleapiclient.discovery import build

from config import GOOGLE_CALENDAR_ID, get_google_credentials, TIMEZONE

class GoogleCalendar:
    def __init__(self):
        self.credentials = get_google_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.calendar_id = GOOGLE_CALENDAR_ID
        self.timezone = TIMEZONE