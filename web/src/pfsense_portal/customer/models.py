from django.db import models


# Create your models here.
class Customer(models.Model):
    # id auto generated
    name = models.CharField(max_length=100)
