from django.shortcuts import render, redirect
from django.views import generic
from .models import *
from django.views import View
from django.utils.timezone import datetime
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views as auth_views
from .forms import NewUserForm, LoginForm
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

today = datetime.today()


# Create your views here.

def get_queryset():
    return Event.objects.filter(status_flag=True)


class EventListView(generic.ListView):
    model = Events
    template_name = 'event/index.html'
    context_object_name = "event_list"
    ordering = ['-startdate']

    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()
        query = self.request.GET.get('q')
        # print("Q....>>>", self.request.GET.get('startdate'))
        # print("Q....>>>", self.request.GET.get('category'))
        category = self.request.GET.get('category', None)
        startdate = self.request.GET.get('startdate', None)
        enddate = self.request.GET.get('enddate', None)
        if query:
            return Events.objects.filter(
                Q(title__icontains=query) |
                Q(location__icontains=query) |
                Q(description__icontains=query)
            )
        elif startdate and enddate:
            queryset = Events.objects.filter(startdate__gte=startdate, enddate__lte=enddate)
        elif category:
            queryset = Events.objects.filter(category=category)
        else:
            queryset = Events.objects.filter(~Q(startdate__gte=now),
                                             ~Q(enddate__lte=now))

        return queryset

    def get_context_data(self, **kwargs):
        queryset = super().get_context_data(**kwargs)
        queryset['category_list'] = Category.objects.all()

        return queryset

    def post(self, request, **kwargs):
        print(request.POST)
        return


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'event/login.html'


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = NewUserForm
    template_name = 'event/registration.html'
    success_url = '/login/'
    success_message = "Registration successful..,login"
    error_message = "Unsuccessful registration. Invalid information"


class UpdateCommentVote(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):

        comment_id = self.kwargs.get('comment_id', None)
        option = self.kwargs.get('option', None)  # like or dislike button clicked
        print("opinion..........>>", option)

        # comment = get_object_or_404(Events, pk=comment_id)
        comment = Events.objects.get(id=comment_id)
        print("----->>", comment)

        try:
            # If child DisLike model doesnot exit then create
            comment.dis_likes
        except Events.dis_likes.RelatedObjectDoesNotExist as identifier:
            DisLike.objects.create(title=comment)

        try:
            # If child Like model doesnot exit then create
            comment.likes
        except Events.likes.RelatedObjectDoesNotExist as identifier:
            Like.objects.create(title=comment)

        if option.lower() == 'like':

            if request.user in comment.likes.users.all():
                comment.likes.users.remove(request.user)
            else:
                comment.likes.users.add(request.user)
                comment.dis_likes.users.remove(request.user)

        elif option.lower() == 'dis_like':

            if request.user in comment.dis_likes.users.all():
                comment.dis_likes.users.remove(request.user)
            else:
                comment.dis_likes.users.add(request.user)
                comment.likes.users.remove(request.user)
        else:
            return HttpResponseRedirect(reverse('event:home'))
        return HttpResponseRedirect(reverse('event:home'))


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        event = Events.objects.get(id=self.kwargs["pk"])
        try:
            event.booked
        except Events.booked.RelatedObjectDoesNotExist as identifier:
            Booked.objects.create(title=event, is_paid=True)
        if request.user in event.booked.users.all():
            print("already booked......>>>>>")
            return
        else:
            event.booked.users.add(request.user)

        YOUR_DOMAIN = self.request.get_host()
        YOUR_DOMAIN = "http://127.0.0.1:8000"  # change in production
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {

                    'name': event.title,
                    'quantity': 1,
                    'currency': 'inr',
                    'amount': 10000,
                },

            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancelled/',
        )
        return redirect(checkout_session.url)


class SuccessView(generic.TemplateView):
    template_name = 'event/success.html'


class CancelledView(generic.TemplateView):
    template_name = 'event/cancelled.html'
