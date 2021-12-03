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
from django.contrib import messages


stripe.api_key = settings.STRIPE_SECRET_KEY

today = datetime.today()


# Create your views here.


class EventListView(generic.ListView):
    """ List of Events"""
    model = Events
    template_name = 'event/index.html'
    context_object_name = "event_list"
    ordering = ['-startdate']

    paginate_by = 1

    def get_queryset(self):
        now = timezone.now()
        query = self.request.GET.get('q')
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


class LoginView(auth_views.LoginView):
    """Login """
    form_class = LoginForm
    template_name = 'event/login.html'


class SignUpView(SuccessMessageMixin, CreateView):
    """User Registration"""
    form_class = NewUserForm
    template_name = 'event/registration.html'
    success_url = '/login/'
    success_message = "Registration successful..,login"
    error_message = "Unsuccessful registration. Invalid information"


class UpdateCommentVote(LoginRequiredMixin, View):
    """Like and Dislike Event"""

    login_url = '/login/'

    def get(self, request, *args, **kwargs):

        event_id = self.kwargs.get('event_id', None)
        option = self.kwargs.get('option', None)  # like or dislike button clicked
        print("opinion..........>>", option)

        # event = get_object_or_404(Events, pk=event_id)
        event = Events.objects.get(id=event_id)
        print("----->>", event)

        try:
            # If child DisLike model doesnot exit then create
            event.dis_likes
        except Events.dis_likes.RelatedObjectDoesNotExist as identifier:
            DisLike.objects.create(title=event)

        try:
            # If child Like model doesnot exit then create
            event.likes
        except Events.likes.RelatedObjectDoesNotExist as identifier:
            Like.objects.create(title=event)

        if option.lower() == 'like':

            if request.user in event.likes.users.all():
                event.likes.users.remove(request.user)
            else:
                event.likes.users.add(request.user)
                event.dis_likes.users.remove(request.user)

        elif option.lower() == 'dis_like':

            if request.user in event.dis_likes.users.all():
                event.dis_likes.users.remove(request.user)
            else:
                event.dis_likes.users.add(request.user)
                event.likes.users.remove(request.user)
        else:
            return HttpResponseRedirect(reverse('event:home'))
        return HttpResponseRedirect(reverse('event:home'))


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    """Stripe Payment """
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        event = Events.objects.get(id=self.kwargs["pk"])
        try:
            event.booked
        except Events.booked.RelatedObjectDoesNotExist as identifier:
            Booked.objects.create(title=event, is_paid=True)
        if request.user in event.booked.users.all():
            print("already booked......>>>>>")
            messages.success(self.request, 'already booked')
            return HttpResponseRedirect(reverse("event:home"))

        else:
            event.booked.users.add(request.user)

        host = self.request.get_host()
        print(host)
        # YOUR_DOMAIN = "http://127.0.0.1:8000"  # change in production
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {

                    'name': event.title,
                    'quantity': 1,
                    'currency': 'inr',
                    'amount': 50000,
                },

            ],
            mode='payment',

            success_url="http://{}{}".format(host, reverse('event:success')),
            cancel_url="http://{}{}".format(host, reverse('event:cancelled')),
        )
        return redirect(checkout_session.url)


class SuccessView(generic.TemplateView):
    template_name = 'event/success.html'


class CancelledView(generic.TemplateView):
    template_name = 'event/cancelled.html'
