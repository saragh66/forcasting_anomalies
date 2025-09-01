from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # login, logout
    path('', include('core.urls', namespace='core')),  # landing page + CSV + anomalies
    path('managers/', include('managers.urls', namespace='managers')), 
    path('analytics/', include('analytics.urls', namespace='analytics')), 
    path('analytics/', include('analytics.urls')),# dashboard manager
   
]

