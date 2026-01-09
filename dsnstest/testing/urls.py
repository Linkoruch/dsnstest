from django.urls import path
from . import views

app_name = "testing"

urlpatterns = [
    path("", views.test_list, name="test_list"),
    path("test/<int:test_id>/start/", views.test_start, name="test_start"),
    path("test/<int:test_id>/take/", views.test_take, name="test_take"),
    path("result/<int:attempt_id>/", views.result_view, name="result"),
]
