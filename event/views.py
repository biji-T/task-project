from django.shortcuts import render
from django.views import generic
from .models import *
from django.utils.timezone import datetime
from django.db.models import Q

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

    #
    # def get_context_data(self, *args, **kwargs):
    #     context = super(EventListView, self).get_context_data(*args, **kwargs)
    #
    #
    #     context['expire'] = Events.objects.all()
    #
    #     return context

    def get_queryset(self):
        now = timezone.now()
        query = self.request.GET.get('q')
        print("Q....>>>", self.request.GET.get('startdate'))
        print("Q....>>>", self.request.GET.get('category'))
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
        #
        # def get_queryset(params):
        #
        #     date_created = params.get('date_created')
        #     keyword = params.get('keyword')
        #     qset = Q(pk__gt=0)
        #     if keyword:
        #         qset &= Q(title__icontains=keyword)
        #     if date_created:
        #         qset &= Q(date_created__gte=date_created)
        #     return qset
        return queryset

    def get_context_data(self, **kwargs):
        queryset = super().get_context_data(**kwargs)
        queryset['category_list'] = Category.objects.all()

        return queryset

    def post(self, request, **kwargs):
        print(request.POST)
        return
