from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
