from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('navigations/', include('app.dashboard.urls')),
    path('announcements/', include('app.announcements.urls')),
    path('accounts/', include('app.accounts.urls')),
    path('', include('app.elections.urls')),
    path('manage-elections/', include('app.manage_elections.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)