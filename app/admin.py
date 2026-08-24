from django.contrib import admin

from app.models import Customer


# Register your models here.
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'dob', 'created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'dob']
