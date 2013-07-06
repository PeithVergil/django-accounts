from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.forms import UserCreationForm, EditUserForm
from accounts.models import User

class CustomUserAdmin(UserAdmin):
	form = EditUserForm

	fieldsets = (
		(None, {
			'fields': ('email',)
		}),
		('Personal info', {
			'fields': ('firstname', 'lastname',)
		}),
		('Permissions', {
			'fields': ('user_permissions', 'groups', 'is_active', 'is_staff',)
		}),
		('Important dates', {
			'fields': ('last_login',)
		}),
	)

	add_form = UserCreationForm

	add_fieldsets = (
		(None, {
			# 'classes': ('wide',),
			'fields': ('email', 'firstname', 'lastname', 'password1', 'password2',)
		}),
	)

	list_display = ('email', 'firstname', 'lastname', 'signup_date',)
	ordering = ('email',)

admin.site.register(User, CustomUserAdmin)