from django.contrib import admin

from app.models import Customer, Policy, PolicyStateHistory


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "dob", "created_at", "updated_at"]
    search_fields = ["first_name", "last_name", "dob"]


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ["id", "type", "premium", "cover", "created_at", "updated_at"]
    search_fields = ["type", "id"]


@admin.register(PolicyStateHistory)
class PolicyStateHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "from_state", "to_state", "changed_at"]
    search_fields = ["from_state", "to_state", "changed_at"]
