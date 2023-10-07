import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import config


class RegisteredIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.ip_address

    def is_within_limit(self):
        return self.amount < config.MAX_PER_IP


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, email=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self,
                         username,
                         password=None,
                         email=None,
                         **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, email, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    servers = models.ManyToManyField('server.Server')
    id = models.AutoField(primary_key=True)
    dms = models.ManyToManyField('dm.DM')
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    def generate_token(self):
        self.token = uuid.uuid4()
        self.save()

    class Meta:
        db_table = 'user_user'
        swappable = 'AUTH_USER_MODEL'
