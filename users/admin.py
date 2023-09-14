from django.contrib import admin
from users.models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'country', 'avatar', 'verified',)
    list_filter = ('verified', 'country')
    search_fields = ('email', 'phone', 'country',)