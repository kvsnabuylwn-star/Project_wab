from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    STATUS_CHOICES = [
        ('available', 'พร้อมส่งต่อ'),
        ('reserved', 'มีคนขอรับแล้ว'),
        ('completed', 'ส่งมอบสำเร็จ'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้ลงประกาศ")
    title = models.CharField(max_length=200, verbose_name="ชื่อสิ่งของ")
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0, verbose_name="ราคา (0 = แจกฟรี)")
    contact_link = models.CharField(max_length=300, blank=True, null=True, verbose_name="ลิงก์ช่องทางติดต่อ")
    image = models.ImageField(upload_to='items/', blank=True, null=True, verbose_name="รูปภาพประกอบ")
    description = models.TextField(verbose_name="รายละเอียดสภาพของ/โน้ต")
    status = models.CharField(max_length=20, default='available', choices=STATUS_CHOICES, verbose_name="สถานะ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ลงประกาศ")

    class Meta:
        verbose_name = "สิ่งของสำหรับส่งต่อ"
        verbose_name_plural = "สิ่งของสำหรับส่งต่อ"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_free(self):
        return self.price == 0

    @property
    def contact_info(self):
        """วิเคราะห์ช่องทางติดต่อ คืนค่าแพลตฟอร์ม ไอคอน สี และ URL สำหรับแสดงผลอย่างสวยงาม"""
        if not self.contact_link:
            return None
        link = self.contact_link.strip()
        if not link:
            return None

        lower = link.lower()

        # Phone check
        phone_digits = link.replace('-', '').replace(' ', '').replace('+', '')
        if lower.startswith('tel:') or (phone_digits.isdigit() and len(phone_digits) in [9, 10]):
            clean_phone = link.replace('tel:', '').strip()
            return {
                'platform': 'phone',
                'name': 'เบอร์โทรศัพท์',
                'display_text': clean_phone,
                'icon': 'fa-solid fa-phone text-emerald-600',
                'icon_bg': 'bg-emerald-100',
                'card_border': 'border-emerald-200 hover:border-emerald-300 bg-emerald-50/40',
                'url': f'tel:{clean_phone.replace("-", "").replace(" ", "")}',
                'badge': 'โทรติดต่อ',
            }

        # Email check
        if lower.startswith('mailto:') or ('@' in lower and '.' in lower and 'http' not in lower and 'line' not in lower and 'fb' not in lower and 'instagram' not in lower):
            clean_email = link.replace('mailto:', '').strip()
            return {
                'platform': 'email',
                'name': 'อีเมล',
                'display_text': clean_email,
                'icon': 'fa-solid fa-envelope text-blue-600',
                'icon_bg': 'bg-blue-100',
                'card_border': 'border-blue-200 hover:border-blue-300 bg-blue-50/40',
                'url': f'mailto:{clean_email}',
                'badge': 'ส่งอีเมล',
            }

        # LINE check
        if 'line.me' in lower or 'lin.ee' in lower or 'line:' in lower or 'line id' in lower or (lower.startswith('@') and '.' not in lower):
            display = link
            url = link
            if not (url.startswith('http://') or url.startswith('https://')):
                clean_id = link.replace('line id:', '').replace('line:', '').strip().lstrip('@')
                url = f'https://line.me/ti/p/~{clean_id}'
                display = f'@{clean_id}'
            else:
                display = 'LINE Official / Profile'
            return {
                'platform': 'line',
                'name': 'LINE',
                'display_text': display,
                'icon': 'fa-brands fa-line text-[#06C755]',
                'icon_bg': 'bg-[#06C755]/15',
                'card_border': 'border-emerald-200 hover:border-emerald-300 bg-emerald-50/40',
                'url': url,
                'badge': 'LINE',
            }

        # Facebook check
        if 'facebook.com' in lower or 'fb.com' in lower or 'fb.me' in lower:
            url = link if (link.startswith('http://') or link.startswith('https://')) else f'https://{link}'
            return {
                'platform': 'facebook',
                'name': 'Facebook',
                'display_text': 'Facebook Profile / Page',
                'icon': 'fa-brands fa-facebook text-[#1877F2]',
                'icon_bg': 'bg-blue-100',
                'card_border': 'border-blue-200 hover:border-blue-300 bg-blue-50/40',
                'url': url,
                'badge': 'Facebook',
            }

        # Instagram check
        if 'instagram.com' in lower or 'instagr.am' in lower or 'ig:' in lower:
            display = 'Instagram'
            url = link
            if not (url.startswith('http://') or url.startswith('https://')):
                handle = link.replace('ig:', '').strip().lstrip('@')
                url = f'https://instagram.com/{handle}'
                display = f'@{handle}'
            else:
                parts = [p for p in url.rstrip('/').split('/') if p]
                if parts and parts[-1] not in ['instagram.com', 'instagr.am', 'www.instagram.com']:
                    display = f'@{parts[-1]}'
            return {
                'platform': 'instagram',
                'name': 'Instagram',
                'display_text': display,
                'icon': 'fa-brands fa-instagram text-[#E4405F]',
                'icon_bg': 'bg-pink-100',
                'card_border': 'border-pink-200 hover:border-pink-300 bg-pink-50/40',
                'url': url,
                'badge': 'Instagram',
            }

        # Twitter / X check
        if 'twitter.com' in lower or 'x.com' in lower:
            url = link if (link.startswith('http://') or link.startswith('https://')) else f'https://{link}'
            return {
                'platform': 'x',
                'name': 'X (Twitter)',
                'display_text': 'X / Twitter Profile',
                'icon': 'fa-brands fa-x-twitter text-gray-900',
                'icon_bg': 'bg-gray-100',
                'card_border': 'border-gray-300 hover:border-gray-400 bg-gray-50/60',
                'url': url,
                'badge': 'X (Twitter)',
            }

        # General URL
        url = link if (link.startswith('http://') or link.startswith('https://')) else f'https://{link}'
        from urllib.parse import urlparse
        domain = 'ลิงก์ภายนอก'
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                domain = parsed.netloc.replace('www.', '')
        except Exception:
            pass

        return {
            'platform': 'web',
            'name': 'เว็บไซต์ / ลิงก์ติดต่อ',
            'display_text': domain,
            'icon': 'fa-solid fa-link text-blue-500',
            'icon_bg': 'bg-blue-100',
            'card_border': 'border-gray-200 hover:border-gray-300 bg-gray-50/60',
            'url': url,
            'badge': domain,
        }


class ClaimRequest(models.Model):
    PICKUP_CHOICES = [
        ('ใต้ตึกคณะ ICT (ลานกิจกรรม)', 'ใต้ตึกคณะ ICT (ลานกิจกรรม)'),
        ('หน้าห้องแล็บ CS ชั้น 2', 'หน้าห้องแล็บ CS ชั้น 2'),
        ('โรงอาหารกลาง / ลานเพลิน', 'โรงอาหารกลาง / ลานเพลิน'),
        ('หน้าร้านกาแฟ / หอสมุด', 'หน้าร้านกาแฟ / หอสมุด'),
        ('นัดหมายผ่านแชทส่วนตัว', 'นัดหมายผ่านแชทส่วนตัว'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="ของที่ขอรับ")
    requester = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้ขอรับ")
    pickup_place = models.CharField(
        max_length=150, 
        choices=PICKUP_CHOICES, 
        default='ใต้ตึกคณะ ICT (ลานกิจกรรม)', 
        verbose_name="จุดนัดรับใต้ตึกสาขา"
    )
    meetup_date = models.DateField(verbose_name="วันที่นัดรับ")
    note = models.TextField(blank=True, verbose_name="ข้อความถึงรุ่นพี่/ผู้ให้")
    is_confirmed = models.BooleanField(default=False, verbose_name="เจ้าของยืนยันการส่งมอบ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ส่งคำขอ")

    class Meta:
        verbose_name = "การขอนัดรับของ"
        verbose_name_plural = "การขอนัดรับของ"
        ordering = ['-created_at']

    def __str__(self):
        return f"คำขอรับ {self.item.title} โดย {self.requester.username}"


class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comments', verbose_name="สิ่งของที่แสดงความเห็น")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name="ผู้แสดงความเห็น")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name="ตอบกลับความคิดเห็น")
    content = models.TextField(verbose_name="ข้อความความคิดเห็น")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่แสดงความเห็น")

    class Meta:
        verbose_name = "ความคิดเห็น"
        verbose_name_plural = "ความคิดเห็น"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username} บน {self.item.title}: {self.content[:30]}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('claim_new', 'มีคำขอนัดรับใหม่'),
        ('claim_confirmed', 'ยืนยันการส่งมอบแล้ว'),
        ('comment_new', 'มีความคิดเห็นใหม่'),
        ('reply_new', 'มีการตอบกลับความคิดเห็น'),
        ('system', 'แจ้งเตือนระบบ'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="ผู้รับการแจ้งเตือน")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications', verbose_name="ผู้ส่ง")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True, verbose_name="สิ่งของที่เกี่ยวข้อง")
    claim = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True, blank=True, verbose_name="คำขอนัดรับ")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, verbose_name="ความคิดเห็น")
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='claim_new', verbose_name="ประเภทการแจ้งเตือน")
    title = models.CharField(max_length=200, verbose_name="หัวข้อ")
    message = models.TextField(verbose_name="ข้อความ")
    is_read = models.BooleanField(default=False, verbose_name="อ่านแล้ว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เวลาที่แจ้งเตือน")

    class Meta:
        verbose_name = "การแจ้งเตือน"
        verbose_name_plural = "การแจ้งเตือน"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username}: {self.title}"


class UserProfile(models.Model):
    YEAR_LEVEL_CHOICES = [
        (1, 'ปี 1'),
        (2, 'ปี 2'),
        (3, 'ปี 3'),
        (4, 'ปี 4'),
    ]

    THEME_MODE_CHOICES = [
        ('light', 'โหมดสว่าง'),
        ('dark', 'โหมดมืด'),
    ]
    ACCENT_COLOR_CHOICES = [
        ('blue', 'CS Blue'),
        ('indigo', 'Royal Indigo'),
        ('emerald', 'Emerald Forest'),
        ('rose', 'Rose Ruby'),
        ('amber', 'Amber Sun'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="ผู้ใช้")
    student_id = models.CharField(max_length=20, blank=True, default="", verbose_name="รหัสนักศึกษา")
    year_level = models.IntegerField(choices=YEAR_LEVEL_CHOICES, default=2, verbose_name="ชั้นปี")
    phone_number = models.CharField(max_length=20, blank=True, default="", verbose_name="เบอร์โทรศัพท์")
    line_id = models.CharField(max_length=50, blank=True, default="", verbose_name="Line ID")
    bio = models.TextField(blank=True, default="", verbose_name="คำแนะนำตัวสั้นๆ")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="รูปโปรไฟล์")
    theme_mode = models.CharField(max_length=20, choices=THEME_MODE_CHOICES, default='light', verbose_name="โหมดธีม")
    accent_color = models.CharField(max_length=20, choices=ACCENT_COLOR_CHOICES, default='blue', verbose_name="สีธีมหลัก")
    notify_email = models.BooleanField(default=True, verbose_name="รับการแจ้งเตือนทางอีเมล")
    show_contact_publicly = models.BooleanField(default=True, verbose_name="แสดงเบอร์โทร/Line ในหน้าประกาศ")

    class Meta:
        verbose_name = "โปรไฟล์ผู้ใช้"
        verbose_name_plural = "โปรไฟล์ผู้ใช้"

    def __str__(self):
        return f"Profile of {self.user.username}"



from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)

