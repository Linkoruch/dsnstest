from django.contrib import admin
from django.urls import path, include
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group

# Заголовки адмінки
admin.site.site_header = "Адміністративна панель"
admin.site.site_title = "Адміністративна панель"
admin.site.index_title = "Керування системою тестування"


def ordered_get_app_list(self, request, app_label=None):
    app_list = AdminSite.get_app_list(self, request, app_label)

    # 1) Порядок секцій (apps)
    app_order = ["testing", "auth"]

    def app_sort_key(app):
        label = app.get("app_label", "")
        return app_order.index(label) if label in app_order else 999

    app_list.sort(key=app_sort_key)

    # 2) Порядок моделей у секції "ЗАГАЛЬНЕ" (testing)
    model_order = ["Test", "Attempt"]  # object_name моделей

    for app in app_list:
        if app.get("app_label") == "testing":
            def model_sort_key(m):
                obj = m.get("object_name", "")
                return model_order.index(obj) if obj in model_order else 999

            app["models"].sort(key=model_sort_key)

    return app_list


admin.site.get_app_list = ordered_get_app_list.__get__(admin.site, AdminSite)

# Прибрати "Групи" з адмін-панелі
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("testing.urls", namespace="testing")),
]
