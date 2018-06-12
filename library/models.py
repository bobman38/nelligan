from django.db import models
from django.conf import settings

# Create your models here.
class Card(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    label = models.CharField(max_length=200)
    code = models.CharField(max_length=200)
    pin = models.CharField(max_length=200)
    lastrefresh = models.DateTimeField()
    fine = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.label

class Library(models.Model):
    code = models.CharField('Code Resa', max_length=10)
    codesearch = models.CharField('Code Search', max_length=10)
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Book(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    duedate = models.DateTimeField('Due Date')
    KIND_CHOICES = (
        (0, 'Loan'),
        (1, 'Hold'),
    )
    fine = models.CharField(max_length=200, null=True)
    kind = models.IntegerField(choices=KIND_CHOICES)
    pickup = models.CharField(max_length=200)
    status = models.CharField(max_length=200, null=True)
    renewed = models.IntegerField(default=0)
    library = models.ForeignKey(Library, null=True)
    def __str__(self):
        return self.name

