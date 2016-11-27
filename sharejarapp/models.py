from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

class Charity(models.Model):
	charityname = models.CharField(max_length=80, unique=True)
	description = models.CharField(max_length=150)
	paypal_email = models.EmailField(unique=True)

	def __unicode__(self):
		return u'{0}'.format(self.charityname)

class Admin(models.Model):
	# Admin user with priviledge to add charity
	user = models.ForeignKey(settings.AUTH_USER_MODEL)

# Just an idea, but maybe include a Log page for admins so that each
# can see who added/updated/deleted a charity
class Log(models.Model):
	ADDED = 'A'
	UPDATED = 'U'
	DELETED = 'D'

	ADMIN_ACTIONS_CHOICES = (
	      (ADDED, 'Added'),
	      (UPDATED, 'Updated'),
		  (DELETED, 'Deleted')
	)

	admin = models.ForeignKey(Admin)
	charity = models.ForeignKey(Charity)

	action = models.CharField(max_length=1,
	                          choices=ADMIN_ACTIONS_CHOICES,
							  default=ADDED)

class Team(models.Model):
	name = models.CharField(max_length=80, unique=True, default='Unknown')
	def __unicode__(self):
		return u'{0}'.format(self.name)


class Member(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	paypal_email = models.EmailField(null=False, blank=False)

class TeamMemberList(models.Model):
	team = models.ForeignKey(Team)
	member = models.ForeignKey(Member)


class Balances(models.Model):
	#username_text = models.CharField(max_length=20, primary_key=True) #FIXLATER add check to make sure username under 20 characters
	member = models.ForeignKey(Member, null=True)
	charity = models.ForeignKey(Charity, null=True)
	#balance = models.DecimalField(max_digits=5, decimal_places=2, default = 0)
	balance = models.DecimalField(max_digits=5, decimal_places=2, default = 0)
	class Meta:
		unique_together = (("member", "charity"))

class Invite(models.Model):
	email = models.EmailField()
	# let Django auto generate this field with a length 6 uuid
	code = models.CharField(max_length=6, unique=True)
	team = models.ForeignKey(Team)
