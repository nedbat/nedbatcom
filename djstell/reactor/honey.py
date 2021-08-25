import time

from django.conf import settings

from .tools import get_client_ip, md5

class Honeypotter:
    FIELDS = [
        "name", "email", "website", "body", "notify", "entryid", "timestamp",
        "honey1", "honey2", "honey3", "honey4",
        "previewcomment", "addcomment", "honeybtn",
        "spinner",
        ]

    def __init__(self, request, entryid):
        self.request = request
        self.entryid = entryid

        self.client_ip = get_client_ip(self.request)

        self.timestamp = None
        self.spinner = None

    def new(self):
        self.timestamp = int(time.time())
        self.make_spinner()

    def make_spinner(self):
        self.spinner = md5(
            self.client_ip,
            self.timestamp,
            self.entryid,
            settings.SECRET_KEY,
            "spinner",
        )

    def field_name(self, field):
        if field == "spinner":
            return "f" + md5(self.client_ip, self.entryid, settings.SECRET_KEY, "spinner_field")
        else:
            return "f" + md5(field, self.spinner, "field")

    def context_data(self):
        data = {
            "spinner": self.spinner,
            "timestamp": self.timestamp,
        }
        for field in self.FIELDS:
            data[f"field_{field}"] = self.field_name(field)
        return data
