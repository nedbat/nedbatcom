import hashlib

from django.conf import settings
from django.db import models

def md5(*parts):
    text = "".join((p or "") for p in parts)
    return hashlib.md5(text.encode("utf-8")).hexdigest()

class Comment(models.Model):
    entryid = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=60)
    email = models.CharField(max_length=100, null=True)
    website = models.CharField(max_length=100, null=True)
    posted = models.DateTimeField(db_index=True)
    body = models.TextField()
    notify = models.BooleanField()

    def gravatar_url(self):
        anum = int(md5(self.email, self.website)[:4], 16) % 282
        email_hash = md5(self.email)
        avhost = "https://nedbatchelder.com"
        default_url = f"{avhost}/pix/avatar/a{anum}.jpg"
        url = f"//www.gravatar.com/avatar/{email_hash}.jpg?default={default_url}&size=80"
        return url


class ReactorRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "reactor":
            return "reactor"
        return None

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "reactor":
            return db == "reactor"
        return None
