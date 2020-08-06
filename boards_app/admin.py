from django.contrib import admin

from . import models
from . import forms
# Register your models here.


#todo before save changes especially to m2m field there should be some kind of pop up confrimation box (like on delete)
# that will inform user that making changes to m2m will affect the relationed baords

@admin.register(models.BoardGroup)
class BoardGroup(admin.ModelAdmin):
    model = models.BoardGroup
    list_display = ("name", "position",)


@admin.register(models.Board)
class Board(admin.ModelAdmin):
    model = models.Board
    form = forms.BoardAdminForm
    list_display = ( "name", "position", "parent", )

