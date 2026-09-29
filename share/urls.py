from django.urls import path
from . import views

urlpatterns = [
    # หน้าหลักและรายการสิ่งของ
    path('', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),

    # ระบบความคิดเห็นและการตอบกลับ (Comments & Replies)
    path('items/<int:item_id>/comments/', views.comment_create, name='comment_create'),
    path('comments/<int:pk>/delete/', views.comment_delete, name='comment_delete'),

    # การขอนัดรับของ
    path('items/<int:item_id>/claim/', views.claim_create, name='claim_create'),
    path('claims/<int:claim_id>/confirm/', views.claim_confirm, name='claim_confirm'),
    path('my-items/', views.my_items, name='my_items'),
    path('my-requests/', views.my_items, name='my_requests'),

    # แดชบอร์ดสรุปสถิติ (Chart.js)
    path('dashboard/', views.dashboard, name='dashboard'),

    # ระบบแจ้งเตือน (Notifications)
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),

    # ระบบผู้ใช้และการตั้งค่า (User, Profile & Settings)
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('api/update-theme/', views.update_theme_api, name='update_theme_api'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('password-change/', views.password_change_view, name='password_change'),
]
