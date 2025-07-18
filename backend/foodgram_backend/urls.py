from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls.authtoken')),  # токены (логин/логаут)
    path('api/', include('recipes.urls')),  # рецепты, теги, ингредиенты
    path('api/', include('djoser.urls')),  # регистрация, смена пароля
    path('api/users/', include('users.urls')),  # профили, аватары, подписки
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
