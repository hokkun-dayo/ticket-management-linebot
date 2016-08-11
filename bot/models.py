from django.db import models


class Message(models.Model):
    mid = models.CharField(max_length=128)
    content = models.CharField(max_length=512)


class Event(models.Model):
    date = models.DateField
    title = models.CharField(max_length=128)
