from typing import Any
from django.db import models

# Create your models here.
class Customer(models.Model):
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=9, blank=True, null=True)
    home = models.CharField(max_length=240, blank=True, null=False)


    def __str__(self) -> str:
        return self.first_name + ' ' + self.last_name


class Tree(models.Model):
    TYPES_OF_TREES = (
        ('SS','świerk srebrny'),
        ('JK','jodła kaukaska'),
    )
    type = models.CharField(max_length=2, choices=TYPES_OF_TREES, default=TYPES_OF_TREES[0][0])
    localization = models.CharField(max_length=300)
    prize = models.IntegerField()


    def __str__(self) -> str:
        return self.type + " " + self.localization + " " + str(self.prize)


class Order(models.Model):
    STATUS = (
        ('1','zapłacone'),
        ('2','zarezerwowane'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    tree = models.ManyToManyField(Tree)
    status = models.CharField(max_length=120, choices=STATUS)
    date = models.DateField(auto_now_add=True)

  
    def __str__(self) -> str:
        return "Zamowienie nr. " + str(self.id)