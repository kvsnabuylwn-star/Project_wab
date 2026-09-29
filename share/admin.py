from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Item, ClaimRequest, Notification, UserProfile, Comment

# Inline UserProfile for UserAdmin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'ข้อมูลโปรไฟล์นักศึกษา'
    verbose_name_plural = 'ข้อมูลโปรไฟล์นักศึกษา (รหัสนักศึกษา / ชั้นปี / ข้อมูลติดต่อ)'
    fields = ('student_id', 'year_level', 'phone_number', 'line_id', 'bio', 'avatar', 'theme_mode', 'accent_color')


# Custom UserAdmin with full control over users
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_full_name_custom', 'email', 'get_student_id', 'get_year_level', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__year_level', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__student_id', 'profile__phone_number')
    ordering = ('-date_joined',)
    actions = ['make_active', 'make_inactive', 'make_staff', 'remove_staff']

    def get_full_name_custom(self, obj):
        return f"{obj.first_name} {obj.last_name}" if (obj.first_name or obj.last_name) else "-"
    get_full_name_custom.short_description = 'ชื่อ - นามสกุล'

    def get_student_id(self, obj):
        return obj.profile.student_id if hasattr(obj, 'profile') and obj.profile.student_id else '-'
    get_student_id.short_description = 'รหัสนักศึกษา'

    def get_year_level(self, obj):
        return f"ปี {obj.profile.year_level}" if hasattr(obj, 'profile') and obj.profile.year_level else '-'
    get_year_level.short_description = 'ชั้นปี'

    @admin.action(description='เปิดใช้งานบัญชีผู้ใช้ที่เลือก (Active)')
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='ระงับการใช้งานบัญชีผู้ใช้ที่เลือก (Inactive)')
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='แต่งตั้งเป็นผู้ดูแลระบบ (Staff)')
    def make_staff(self, request, queryset):
        queryset.update(is_staff=True)

    @admin.action(description='ถอดถอนสิทธิ์ผู้ดูแลระบบ (Remove Staff)')
    def remove_staff(self, request, queryset):
        queryset.update(is_staff=False)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'year_level', 'phone_number', 'line_id', 'theme_mode')
    list_filter = ('year_level', 'theme_mode')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'student_id', 'phone_number', 'line_id')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'owner__username', 'owner__first_name')
    ordering = ('-created_at',)


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('item', 'requester', 'meetup_date', 'pickup_place', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed', 'meetup_date', 'created_at')
    search_fields = ('item__title', 'requester__username', 'pickup_place')
    ordering = ('-created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'title', 'message')
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'item', 'parent', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author__username', 'item__title', 'content')
    ordering = ('-created_at',)

