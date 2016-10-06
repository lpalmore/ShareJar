from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
class Balances(models.Model):
	#username_text = models.CharField(max_length=20, primary_key=True) #FIXLATER add check to make sure username under 20 characters
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	#balance = models.DecimalField(max_digits=5, decimal_places=2, default = 0)
	balance = models.DecimalField(max_digits=5, decimal_places=2, default = 0)