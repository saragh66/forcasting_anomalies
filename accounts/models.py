from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    RH = "RH"
    MANAGER = "MANAGER"
    ROLE_CHOICES = [(RH, "RH"), (MANAGER, "Manager")]
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=RH)

    # Pour les managers : leur email officiel entreprise
    work_email = models.EmailField(blank=True, null=True)

    def is_rh(self):
        return self.role == self.RH

    def is_manager(self):
        return self.role == self.MANAGER
