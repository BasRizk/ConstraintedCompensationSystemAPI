"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
# from rest_framework import routers
# from django.conf import settings
# from django.conf.urls.static import static
from api import views
# from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # path('all_slots', views.AllSlots.as_view()),
    path('all_slots/<str:group_name>', views.AllSlots.as_view()),
    path('all_slots/<str:group_name>/<int:week>', views.AllSlots.as_view()),
    path('all_groups', views.AllGroups.as_view()),
    path('compensate/', views.CompensateSlot.as_view()),
]
#   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns = [
#     # path('admin/', admin.site.urls),
#     path('', include(ROUTER.urls)),
#     # path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]

# urlpatterns = format_suffix_patterns(urlpatterns)
