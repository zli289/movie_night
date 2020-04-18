from django.contrib import admin

# Register your models here.
from .import models
admin.site.register(models.User)
admin.site.register(models.Group)
admin.site.register(models.Membership)
admin.site.register(models.Movie)
admin.site.register(models.Event)
admin.site.register(models.Voting)
admin.site.register(models.Votes)
admin.site.register(models.HasVoted)