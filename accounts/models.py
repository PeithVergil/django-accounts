from django.contrib.auth.models import (
	BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.db import models

class UserManager(BaseUserManager):
	def __new_user(self, email, firstname, lastname, password):
		email = UserManager.normalize_email(email)

		user = self.model(
			firstname=firstname,
			lastname=lastname,
			email=email,
		)
		
		user.set_password(password)

		return user

	def create_user(self, email, firstname, lastname, password):
		"""Create a new user."""

		user = self.__new_user(
			firstname=firstname,
			lastname=lastname,
			password=password,
			email=email,
		)

		user.save(using=self._db)

		return user

	def create_superuser(self, email, firstname, lastname, password):
		"""Create a new admin user."""

		user = self.__new_user(
			firstname=firstname,
			lastname=lastname,
			password=password,
			email=email,
		)

		# Set root user
		user.is_superuser = True
		user.is_active = True
		user.is_staff = True

		user.save(using=self._db)

		return user

class User(AbstractBaseUser, PermissionsMixin):
	# Date the account was created
	signup_date = models.DateTimeField(verbose_name=_('registration date'), auto_now_add=True)

	firstname = models.CharField(verbose_name=_('first name'), max_length=60)
	lastname = models.CharField(verbose_name=_('last name'), max_length=60)

	email = models.EmailField(verbose_name=_('email address'), max_length=255, unique=True, db_index=True)

	is_active = models.BooleanField(verbose_name=_('active status'), default=False)
	is_staff = models.BooleanField(verbose_name=_('staff status'), default=False)

	objects = UserManager()

	REQUIRED_FIELDS = [
		'firstname', 'lastname'
	]
	USERNAME_FIELD = 'email'

	def __unicode__(self):
		return '%s %s %s' % (self.email, self.firstname, self.lastname)

	def get_full_name(self):
		return '%s %s' % (self.firstname, self.lastname)

	def get_short_name(self):
		return self.firstname

	def email_user(self, subject, message, from_email=None):
		send_mail(subject, message, from_email, [self.email])

class Activation(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	code = models.CharField(max_length=64)
	used = models.BooleanField(default=False)
	date = models.DateTimeField(auto_now_add=True)

	#
	# TODO: Add this field
	#
	# date_used = models.DateTimeField()

	class Meta:
		unique_together = ('user', 'code')