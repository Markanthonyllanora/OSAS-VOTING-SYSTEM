from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('navigations/', include('app.dashboard.urls')),
    path('elections/', include('app.elections.urls')),
]