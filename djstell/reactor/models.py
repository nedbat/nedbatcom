from django.db import models

class Comment(models.Model):
    entryid = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=60)
    email = models.CharField(max_length=100, null=True)
    website = models.CharField(max_length=100, null=True)
    posted = models.DateTimeField(db_index=True)
    body = models.TextField()
    notify = models.BooleanField()


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
