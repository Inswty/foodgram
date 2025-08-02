from django.urls import path

from .views import redirect_short_link

urlpatterns = [
    path('s/<str:short_code>/', redirect_short_link, name='recipe_short_link'),
]
