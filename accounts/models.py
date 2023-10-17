from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, validators=[EmailValidator()])

    def clean(self):
        super().clean()
        self.email = self.email.lower()

    def save(self, *args, **kwargs):
        # Hashear la contraseña al guardar el usuario
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
