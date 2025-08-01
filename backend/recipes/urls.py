from django.urls import path
from django.views.generic import TemplateView

from .views import redirect_short_link

urlpatterns = [
    path('s/<str:short_code>/', redirect_short_link, name='recipe_short_link'),
]
"""path('recipes/<int:pk>/',
         TemplateView.as_view(template_name='index.html'),
         name='recipe-detail'
         ),"""