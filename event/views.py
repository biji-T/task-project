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
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
import stripe
import json
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404

stripe.api_key = settings.STRIPE_SECRET_KEY

today = datetime.today()


# Create your views here.


class EventListView(generic.ListView):
    """ List of Events"""
    model = Events
    template_name = 'event/index.html'
    context_object_name = "event_list"
    paginate_by = 10

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
    redirect_field_name = 'next'

    def post(self, request):
        print(request.POST)
        content_id = request.POST.get("content_id", None)
        option = request.POST.get("operation", None)
        print("operation..........>>", option)
        print("content_id....2......>>", content_id)

        # event = get_object_or_404(Events, pk=event_id)
        event = get_object_or_404(Events, pk=content_id)
        print(event)
        # event = Events.objects.get(id=event_id)
        print("----->>", event)

        try:
            # If child DisLike model doesnot exit then create
            event.dis_likes
        except Events.dis_likes.RelatedObjectDoesNotExist as identifier:
            DisLike.objects.create(event=event)

        try:
            # If child Like model doesnot exit then create
            event.likes
        except Events.likes.RelatedObjectDoesNotExist as identifier:
            Like.objects.create(event=event)

        if option.lower() == 'like':

            if request.user in event.likes.users.all():
                event.likes.users.remove(request.user)
                liked = False
                disliked = ''
            else:
                event.likes.users.add(request.user)
                event.dis_likes.users.remove(request.user)
                liked = True
                disliked = False

        elif option.lower() == 'dis_like':

            if request.user in event.dis_likes.users.all():
                event.dis_likes.users.remove(request.user)
                disliked = False
                liked = ''
            else:
                event.dis_likes.users.add(request.user)
                event.likes.users.remove(request.user)
                disliked = True
                liked = False
        else:
            return HttpResponseRedirect(reverse('event:home'))

        ctx = {"likes_count": event.get_total_likes(), "liked": liked, "content_id": content_id,
               "dislike_count": event.get_total_dis_likes(), "disliked": disliked}
        print(ctx)
        return HttpResponse(json.dumps(ctx), content_type='application/json')


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    """Stripe Payment """
    login_url = '/login/'
    redirect_field_name = 'next'

    def post(self, request, *args, **kwargs):
        event = Events.objects.get(id=self.kwargs["pk"])
        try:
            event.booked
        except Events.booked.RelatedObjectDoesNotExist as identifier:
            Booked.objects.create(event=event, is_paid=True)
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


class FavoriteEventView(generic.ListView):
    template_name = 'event/fav_event.html'
    model = Like

    def get_queryset(self):
        context = Like.objects.filter(users=self.request.user)
        return context
