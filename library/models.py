from django.db import models
from django.conf import settings

# Create your models here.
class Card(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    label = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    pin = models.CharField(max_length=200)
    lastrefresh = models.DateTimeField()
    def __str__(self):
        return self.label

class Book(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    duedate = models.DateTimeField('Due Date')
