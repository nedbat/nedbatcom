import datetime
import time

from django.conf import settings

from .clean import clean_html
from .mail import send_owner_email, send_watcher_emails
from .models import Comment
from .tools import get_client_ip, md5
from .valid import valid_email, valid_name, valid_website

class Honeypotter:
    FIELDS = ["spinner", "entryid", "timestamp"]

    def __init__(self, request, entryid):
        self.request = request
        self.entryid = entryid

        self.is_post = (request.method == "POST")
        self.client_ip = get_client_ip(self.request)
        self.errormsgs = []

        if self.is_post:
            self._init_post()
        else:
            self._init_get()

    def field_name(self, field):
        assert field in self.FIELDS
        if field == "spinner":
            return "f" + md5(self.client_ip, self.entryid, settings.SECRET_KEY, "spinner_field")
        else:
            return "f" + md5(field, self.spinner, "field")

    def context_data(self):
        data = {
            "spinner": self.spinner,
            "timestamp": int(time.time()),
            "entryid": self.entryid,
            "errormsgs": self.errormsgs,
        }
        for field in self.FIELDS:
            data[f"field_{field}"] = self.field_name(field)
        return data

    def _init_get(self):
        self.timestamp = int(time.time())
        self.spinner = md5(
            self.client_ip,
            self.timestamp,
            self.entryid,
            settings.SECRET_KEY,
            "spinner",
        )

    def _init_post(self):
        self.spinner = self.field_value("spinner")
        if not self.spinner:
            self.add_error("Something is wrong with the spinner")

        now = int(time.time())
        try:
            self.timestamp = int(self.field_value("timestamp"))
        except ValueError:
            self.add_error("Something is wrong with the timestamp")
            self.timestamp = 0
        else:
            now = time.time()
            age = now - self.timestamp
            if age < 0:
                self.add_error("A post from the future!")
            if age > 30*60:
                self.add_error("You took a long time entering this post. Please preview it and submit it again.")

    def add_error(self, message):
        self.errormsgs.append(message)

    def field_value(self, field):
        return self.request.POST.get(self.field_name(field), "")

    def pushed_button(self, btnname):
        """Did the user push the `btnname` button?"""
        return self.field_value(btnname) != ""

    def handle_post(self, context):
        # print("\n".join(f"{k!r}: {v!r}" for k, v in self.request.POST.items()))
        if self.field_value("entryid") != self.entryid:
            self.add_error("Posting to the wrong entry")

        if any(self.field_value(fname) for fname in self.FIELDS if fname.startswith("honey")):
            self.add_error("Go away stupid bear")


class CommentForm(Honeypotter):
    FIELDS = Honeypotter.FIELDS + [
        "name", "email", "website", "body", "notify",
        "honey1", "honey2", "honey3", "honey4",
        "previewbtn", "addbtn", "honeybtn",
    ]

    def context_data(self):
        data = super().context_data()
        data.update({
            "name": self.request.session.get("name", ""),
            "email": self.request.session.get("email", ""),
            "website": self.request.session.get("website", ""),
            "notify": self.request.session.get("notify", False),
        })
        return data

    def handle_post(self, context):
        super().handle_post(context)

        self.latest_name = self.field_value("name").strip()
        self.latest_email = self.field_value("email").strip()
        self.latest_website = self.field_value("website").strip()
        self.latest_body = clean_html(self.field_value("body"))
        self.latest_notify = (self.field_value("notify") == "on")

        self.request.session["name"] = self.latest_name
        self.request.session["email"] = self.latest_email
        self.request.session["website"] = self.latest_website
        self.request.session["notify"] = self.latest_notify

        self.is_previewing = self.pushed_button("previewbtn")
        self.is_adding = self.pushed_button("addbtn")

        if not self.latest_name:
            self.add_error("You must provide a name.")

        if (not self.latest_email) and (not self.latest_website):
            self.add_error("You must provide either an email or a website.")

        if self.latest_name and not valid_name(self.latest_name):
            self.add_error("That doesn't look like a real name.")

        if self.latest_email and not valid_email(self.latest_email):
            self.add_error("That doesn't look like a valid email.")

        if self.latest_website and not valid_website(self.latest_website):
            self.add_error("That doesn't look like a valid web site.")

        if not self.latest_body:
            self.add_error("You didn't write a comment!")

        if self.latest_body.count("<a href=") > 4:
            self.add_error("Too many links is suspicious")

        if self.latest_notify and not self.latest_email:
            self.add_error("You can't get future comments if you don't provide an email.")

        if self.is_previewing:
            context["body"] = self.latest_body

        if not self.errormsgs:
            if self.is_previewing:
                context["preview"] = {
                    "website": self.latest_website,
                    "name": self.latest_name,
                    "posted": datetime.datetime.now(),
                    "body": self.latest_body,
                }
            elif self.is_adding:
                com = self.comment_object()
                com.save()
                send_owner_email(com, dict(context.flatten()))
                send_watcher_emails(com, dict(context.flatten()))
            else:
                raise Exception("Shouldn't something be happening?")

    def comment_object(self):
        return Comment(
            entryid=self.entryid,
            name=self.latest_name,
            email=self.latest_email,
            website=self.latest_website,
            posted=datetime.datetime.now(),
            body=self.latest_body,
            notify=self.latest_notify,
        )
