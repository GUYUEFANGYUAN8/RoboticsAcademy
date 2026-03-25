"""Admin registrations for Robotics Academy models."""

from django.contrib import admin
from .models import Exercise, Universe, World, Tool, Robot

from django.contrib import admin

# Register your models here.


class SaveExAdmin(admin.ModelAdmin):
    """Admin configuration for exercise entries."""

    change_list_template = "./admin/change_list_ex.html"


class SaveUnivAdmin(admin.ModelAdmin):
    """Admin configuration shared by universe-related entries."""

    change_list_template = "./admin/change_list_univ.html"


admin.site.register(Exercise, SaveExAdmin)
admin.site.register(Tool, SaveUnivAdmin)
admin.site.register(Universe, SaveUnivAdmin)
admin.site.register(World, SaveUnivAdmin)
admin.site.register(Robot, SaveUnivAdmin)
