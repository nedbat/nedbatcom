import datetime
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
        self.errormsgs = []

        self.is_post = (self.request.method == "POST")
        if self.is_post:
            self.spinner = self.field_value("spinner")
            self.timestamp = self.field_value("timestamp")
            self.is_previewing = self.pushed_button("previewcomment")
        else:
            self.timestamp = int(time.time())
            self.spinner = md5(
                self.client_ip,
                self.timestamp,
                self.entryid,
                settings.SECRET_KEY,
                "spinner",
            )

    def field_value(self, field):
        assert self.is_post
        return self.request.POST.get(self.field_name(field), "")

    def field_name(self, field):
        if field == "spinner":
            return "f" + md5(self.client_ip, self.entryid, settings.SECRET_KEY, "spinner_field")
        else:
            return "f" + md5(field, self.spinner, "field")

    def pushed_button(self, btnname):
        """Did the user push the `btnname` button?"""
        return self.is_post and self.field_value(btnname) != ""

    def add_error(self, message):
        self.errormsgs.append(message)

    def context_data(self):
        data = {
            "spinner": self.spinner,
            "timestamp": self.timestamp,
            "errormsgs": self.errormsgs,
            "username": self.request.session.get("name", ""),
            "useremail": self.request.session.get("email", ""),
            "userpage": self.request.session.get("website", ""),
        }
        for field in self.FIELDS:
            data[f"field_{field}"] = self.field_name(field)
        return data

    def handle_post(self, context):
        #print("\n".join(f"{k!r}: {v!r}" for k, v in self.request.POST.items()))
        self.latest_name = self.field_value("name")
        self.latest_email = self.field_value("email")
        self.latest_website = self.field_value("website")
        self.latest_body = self.field_value("body")

        self.request.session["name"] = self.latest_name
        self.request.session["email"] = self.latest_email
        self.request.session["website"] = self.latest_website
        context["body"] = self.latest_body

        if self.is_previewing:
            if not self.latest_name:
                self.add_error("You must provide a name.")

            if (not self.latest_email) and (not self.latest_website):
                self.add_error("You must provide either an email or a website.")

            if not self.latest_body:
                self.add_error("You didn't write a comment!")

            if not self.errormsgs:
                context["preview"] = {
                    "website": self.latest_website,
                    "name": self.latest_name,
                    "posted": datetime.datetime.now(),
                    "body": self.latest_body,
                }
