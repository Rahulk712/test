from django.urls import path, re_path
from django.conf.urls import url, include
from apis import views as apis_views
from apis import email_reader

app_name="apis"

urlpatterns = [
        path('', apis_views.first_view, name="first_view"),
        url(r'^get_emails/', email_reader.getEmails, name="get_emails"),

    ]