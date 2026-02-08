from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('profile_image', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('profile_image', 'bio')}),
    )
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile_image')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name')

# @admin.register(CustomUser)
# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal Info', {'fields': ('first_name',
#          'last_name', 'email', 'bio', 'profile_image')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff',
#          'is_superuser', 'groups', 'user_permissions')}),
#         ('Importants Dates', {'fields': ('last_login', 'date_joined')})
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide'),
#             'fields': ('username', 'password1', 'password2', 'email', 'bio', 'profile_image')
#         })
#     )

#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     ordering = ('-username',)