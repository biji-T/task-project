from django.contrib import admin
from .models import Events, Booked, Category, Like, DisLike


# Register your models here.


class EventsAdmin(admin.ModelAdmin):
    list_display = ('title', 'startdate', 'enddate', 'published')
    list_filter = ['category', 'startdate', 'enddate']
    search_fields = ['title', 'description']


admin.site.register(Events, EventsAdmin),
admin.site.register(Like),
admin.site.register(DisLike),
admin.site.register(Category),
admin.site.register(Booked),
