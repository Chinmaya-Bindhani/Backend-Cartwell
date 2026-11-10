from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import  RefreshToken
from ..models import CustomUser
from ..otp_Service import verify_otp


def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh":str(refresh),
        "access":str(refresh.access_token)
    }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,min_length=8)
    class Meta:
        model = CustomUser
        fields=['email','phone_number','username','first_name','last_name','password']

    def validate(self, data):
        data['email'] = data.get("email") or None
        data["phone_number"] = data.get("phone_number") or None
        if not data["email"] and not data["phone_number"]:
            raise serializers.ValidationError("email or phone number is required ")
        return data

    def create(self, validated_data):
        return CustomUser.objects.create_user(is_active=False,**validated_data)


class VerifyOtpSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    otp = serializers.CharField(min_length=6,max_length=6)

    def validate(self, attrs):
        user = (CustomUser.objects.filter(email__iexact=attrs["identifier"]).first()
                or CustomUser.objects.filter(phone_number = attrs["identifier"]).first())
        if not user or not verify_otp("register",attrs["identifier"],attrs["otp"]):
            raise serializers.ValidationError("invalid or expired otp ")
        attrs["user"] = user
        return attrs
    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.is_active = True
        user.save(update_fields =["is_active"])
        return get_tokens(user)

class LoginSerializer(serializers.Serializer):
    identifier= serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self,data):
        user = authenticate(
            request=self.context.get("request"),
            username = data["identifier"],
            password = data["password"]
        )

        if not user:
            raise serializers.ValidationError("invalid credentials ")
        data["tokens"]=get_tokens(user)
        return data


