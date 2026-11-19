from django.urls import path
from .views import RegisterView, VerifyOtpView, LoginView,SellerApplicationCreateView,MySellerApplicationView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-otp/", VerifyOtpView.as_view()),
    path("login/", LoginView.as_view()),
    path("seller-applications/",SellerApplicationCreateView.as_view(),),
    path("seller-applications/me/",MySellerApplicationView.as_view(),)
]