from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager




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
    email = models.EmailField(max_length=255, unique=True,null=True, verbose_name='Email')
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    username = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','username']


