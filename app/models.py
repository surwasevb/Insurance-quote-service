import uuid

from django.db import models

# Customer model to store customer related data
class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
