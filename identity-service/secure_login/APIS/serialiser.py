from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import  RefreshToken
from ..models import CustomUser,SellerApplicationModel
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

class SellerApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =SellerApplicationModel
        fields = "__all__"

    def validate(self, attrs):
        user = self.context["request"].user
        if user.role != CustomUser.Role.CUSTOMER:
            raise serializers.ValidationError(
                "only existing customers can apply for seller account "
            )
        if SellerApplicationModel.objects.filter(user=user).exists():
            raise serializers.ValidationError(
                "you have already submitted a seller application"

            )

    def create(self, validated_data):
        user = self.context['request'].user
        return SellerApplicationModel.objects.create(
            user = user,
            **validated_data
        )
class SellerApplicationDetailSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    reviewed_by_email = serializers.EmailField(
        source="reviewed_by.email",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = SellerApplicationModel
        fields = [
            "id",
            "user_id",
            "user_email",
            "business_name",
            "business_address",
            "tax_identifier",
            "document_url",
            "status",
            "reviewed_by_email",
            "reviewed_at",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields