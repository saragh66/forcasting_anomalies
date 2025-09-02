from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # login, logout
    path('', include('core.urls', namespace='core')),  # landing page + CSV + anomalies
    path('managers/', include('managers.urls', namespace='managers')),
    path('analytics/', include('analytics.urls', namespace='analytics')), 
    path('analytics/', include('analytics.urls')),# dashboard manager
   
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

