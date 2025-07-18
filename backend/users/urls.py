from django.urls import include, path

from .views import UserAvatarUpdateView  #SubscriptionsView, UserDetailView, SetPasswordView

urlpatterns = [
    path('me/avatar/', UserAvatarUpdateView.as_view(), name='avatar-update'),
    #path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
    #path('set_password/', SetPasswordView.as_view(), name='set-password'),  # если кастомный
    #path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
]
