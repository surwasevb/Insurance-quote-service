import uuid

from django.db import models

# Customer model to store customer related data
class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PolicyState(models.TextChoices):
    NEW = 'new', 'New'
    QUOTED = 'quoted', 'Quoted'
    BOUND = 'bound', 'Bound'
    ACTIVE = 'active', 'Active'
    ACCEPTED = 'accepted', 'Accepted'

class Policy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='policies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=100)
    premium = models.IntegerField(default=0)
    cover = models.IntegerField(default=0)
    state = models.CharField(max_length=100, default=PolicyState.NEW, choices=PolicyState.choices)

    def __str__(self):
        return f"{self.type} {self.customer}"


class PolicyStateHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='state_history'
    )
    from_state = models.CharField(max_length=100, choices=PolicyState.choices)
    to_state = models.CharField(max_length=100,choices=PolicyState.choices)
    changed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
