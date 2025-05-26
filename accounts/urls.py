from django.urls import path
from .views import SignupView, MyProfileView, KakaoLoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MyProfileView.as_view(), name="my_profile"),
    path('kakao/login/', KakaoLoginView.as_view(), name='kakao-login'),
]