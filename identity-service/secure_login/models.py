from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import  timezone

# CUSTOM USER MANAGER USING BASE_USER_MANAGER FROM AUTH.BASE_USER PRE-MODULE
class CustomUserManager(BaseUserManager):
    def create_user(self,email,username,password,phone_number=None,**extra_fields):
        if not email and not phone_number :
            raise ValueError("email or phone number is required")
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email,username=username,phone_number=phone_number,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_superuser',True)
        return self.create_user(email,username,password,**extra_fields)


#CUSTOM USERMODEL FOR EMAIL AND MOBILE AUTHENTICATIONS
class CustomUser(AbstractBaseUser,PermissionsMixin):
    class Role(models.TextChoices):
        CUSTOMER = "customer","Customer",
        SELLER = "seller","Seller",
        ADMIN = "admin","Admin"
    email = models.EmailField(max_length=255, unique=True,null=True, verbose_name='Email')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    username = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default= Role.CUSTOMER
    )

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','username']

class SellerApplicationModel(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending","Pending",
        APPROVED = "approved","Approved",
        REJECTED = "rejected","Rejected"

    user = models.OneToOneField(
        CustomUser,on_delete=models.CASCADE,
        related_name="seller_application"
    )

    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    aadhaar_number = models.CharField(max_length=12)
    pan_number = models.CharField(max_length=10)
    gstin_number = models.CharField(max_length=15,blank=True,)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    reviewed_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_seller_applications",
    )

    reviewed_at = models.DateTimeField(null=True,blank=True)
    rejection_reason = models.CharField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering =["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.business_name} - {self.status}"