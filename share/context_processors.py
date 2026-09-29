from .models import Notification

def notification_context(request):
    """
    Context processor เพื่อให้ข้อมูลการแจ้งเตือนและจำนวนที่ยังไม่ได้อ่าน
    แสดงผลได้ทุกหน้าที่ใช้ base.html
    """
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(
            recipient=request.user
        ).select_related('sender', 'item', 'claim').order_by('-created_at')[:10]
        
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        return {
            'notifications_list': user_notifications,
            'unread_notifications_count': unread_count,
        }
    
    return {
        'notifications_list': [],
        'unread_notifications_count': 0,
    }
