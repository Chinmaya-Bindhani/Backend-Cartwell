import requests
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .throttle import LoginRateThrottle,RegisterRateThrottle


from .serialiser import RegisterSerializer, VerifyOtpSerializer, LoginSerializer
from ..otp_Service import generate_otp


def send_sms(phone, message):
    if not settings.FAST2SMS_KEY:
        print(f"[SMS to {phone}] {message}")      # dev fallback
        return
    requests.post(
        "https://www.fast2sms.com/dev/bulkV2",
        headers={"authorization": settings.FAST2SMS_KEY},
        data={"route": "q", "message": message,
              "numbers": phone[-10:], "language": "english"},
        timeout=10,
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        identifier = user.email or user.phone_number
        otp = generate_otp("register", identifier)

        if user.email:
            send_mail("Your OTP", f"Your code is {otp}. Valid for 5 minutes.", None, [user.email])
        else:
            send_sms(user.phone_number, f"Your OTP is {otp}. Valid for 5 minutes.")

        return Response({"message": "OTP sent", "identifier": identifier},
                        status=status.HTTP_201_CREATED)


class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())        # activates user, returns JWT


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data["tokens"])