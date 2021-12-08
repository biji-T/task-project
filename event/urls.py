from django.conf.urls import url
from django.urls import path, re_path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'event'

urlpatterns = [
    path('', views.EventListView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    path("register", views.SignUpView.as_view(), name="register"),
    path('reaction/', views.UpdateCommentVote.as_view(), name='reaction'),
    # path('reaction/<int:comment_id>/<str:option>', views.UpdateCommentVote.as_view(), name='event_reaction'),
    path('create-checkout-session/<pk>/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('cancelled/', views.CancelledView.as_view(), name='cancelled'),
    path('fav-event/', views.FavoriteEventView.as_view(), name='fav-event'),

]
