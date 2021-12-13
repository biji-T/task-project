from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.contrib import admin


# Create your models here.

class BaseModel(models.Model):
    """Model for subclassing."""

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status_flag = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name


class Events(BaseModel):
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True)
    location = models.CharField(max_length=200, null=False, blank=False)
    startdate = models.DateTimeField(null=True)
    enddate = models.DateTimeField(null=True)
    cover = models.ImageField(upload_to='images/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    def published(self):
        now = timezone.now()
        if self.enddate < now:
            return True
        return False

    def get_total_likes(self):
        return self.likes.users.count()

    def get_total_dis_likes(self):
        return self.dis_likes.users.count()

    #
    # def get_display_price(self):
    #     return "{0:.2f}".format(self.price / 100)

    class Meta:
        ordering = ['-startdate']
        verbose_name = 'Event'


class Booked(BaseModel):
    """ book  event """

    event = models.OneToOneField(Events, related_name="booked", on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='requirement_booked')
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event)[:30]


class Like(BaseModel):
    """ like  event """

    event = models.OneToOneField(Events, related_name="likes", on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='requirement_likes', through='ClassMate')
    liked_on = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    def __str__(self):
        return str(self.event)[:30]


class DisLike(BaseModel):
    """ Dislike  event """

    event = models.OneToOneField(Events, related_name="dis_likes", on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='requirement_dis_likes')

    def __str__(self):
        return str(self.event)[:30]
