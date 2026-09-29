from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse

from .models import Item, ClaimRequest, Notification, UserProfile, Comment
from .forms import (
    RegisterForm, ItemForm, ClaimRequestForm, ClaimConfirmForm, 
    UserUpdateForm, UserProfileForm, UserSettingsForm,
    UserPasswordChangeForm, UserPasswordResetForm
)


# ==========================================
# 1. Authentication Views
# ==========================================

def register_view(request):
    """ฟังก์ชันสมัครสมาชิกด้วย RegisterForm (สืบทอดจาก UserCreationForm)"""
    if request.user.is_authenticated:
        return redirect('item_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"ลงทะเบียนบัญชี {user.username} สำเร็จเรียบร้อยแล้ว กรุณาเข้าสู่ระบบ")
            return redirect('login')
        else:
            messages.error(request, "ข้อมูลการสมัครไม่ถูกต้อง กรุณาตรวจสอบข้อผิดพลาดด้านล่าง")
    else:
        form = RegisterForm()

    return render(request, 'share/register.html', {'form': form})


def login_view(request):
    """ฟังก์ชันเข้าสู่ระบบด้วย AuthenticationForm และฟังก์ชัน authenticate/login"""
    if request.user.is_authenticated:
        return redirect('item_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"ยินดีต้อนรับคุณ {user.first_name or user.username} เข้าสู่ระบบ!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('item_list')
            else:
                messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    else:
        form = AuthenticationForm()

    return render(request, 'share/login.html', {'form': form})


def logout_view(request):
    """ฟังก์ชันออกจากระบบ"""
    logout(request)
    messages.info(request, "คุณได้ออกจากระบบเรียบร้อยแล้ว")
    return redirect('login')


def password_reset_view(request):
    """ฟังก์ชันรีเซ็ตรหัสผ่านสำหรับผู้ใช้ที่ลืมรหัสผ่าน (Reset Password)"""
    if request.user.is_authenticated:
        return redirect('item_list')

    if request.method == 'POST':
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            new_password = form.cleaned_data.get('new_password1')

            user = User.objects.filter(Q(username=username) | Q(profile__student_id=username), email=email).first()
            if user:
                user.set_password(new_password)
                user.save()
                messages.success(request, f"ตั้งรหัสผ่านใหม่สำหรับบัญชี {user.username} สำเร็จเรียบร้อยแล้ว กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่")
                return redirect('login')
            else:
                messages.error(request, "ไม่พบบัญชีผู้ใช้ที่มีชื่อผู้ใช้/รหัสนักศึกษา และอีเมลนี้ในระบบ")
    else:
        form = UserPasswordResetForm()

    return render(request, 'share/password_reset.html', {'form': form})


@login_required
def password_change_view(request):
    """ฟังก์ชันเปลี่ยนรหัสผ่านสำหรับผู้ใช้ที่เข้าสู่ระบบอยู่ (Change Password)"""
    if request.method == 'POST':
        form = UserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "เปลี่ยนรหัสผ่านสำเร็จเรียบร้อยแล้ว!")
            return redirect('profile')
        else:
            messages.error(request, "ข้อมูลรหัสผ่านไม่ถูกต้อง กรุณาตรวจสอบข้อผิดพลาดด้านล่าง")
    else:
        form = UserPasswordChangeForm(user=request.user)

    return render(request, 'share/password_change.html', {'form': form})



# ==========================================
# 2. Item Views (รายการ, รายละเอียด, เพิ่ม, แก้ไข, ลบ)
# ==========================================

def item_list(request):
    """
    แสดงรายการของทั้งหมด พร้อมระบบ Search ตามชื่อ/รายละเอียด และกรองตามสถานะ
    """
    items = Item.objects.select_related('owner').all()

    # การค้นหา (Search)
    search_query = request.GET.get('q', '').strip()
    if search_query:
        items = items.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # กรองตามสถานะ (Status Filter)
    status_filter = request.GET.get('status', '')
    if status_filter:
        items = items.filter(status=status_filter)
    else:
        # โดยค่าเริ่มต้นในหน้าหลัก จะไม่แสดงรายการที่ส่งมอบสำเร็จแล้ว (completed) ให้ดูได้ในประวัติเท่านั้น
        items = items.exclude(status='completed')

    # รายการประกาศล่าสุดสำหรับกล่องฝั่งขวา (5 รายการล่าสุดที่ไม่ใช่ completed)
    recent_items = Item.objects.select_related('owner').exclude(status='completed').order_by('-created_at')[:5]

    context = {
        'items': items,
        'recent_items': recent_items,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'index.html', context)


def item_detail(request, pk):
    """แสดงรายละเอียดสิ่งของ และปุ่มกดขอรับของ พร้อมระบบความคิดเห็น/ตอบกลับ"""
    item = get_object_or_404(Item.objects.select_related('owner'), pk=pk)
    
    # ตรวจสอบว่าผู้ใช้ปัจจุบันได้ส่งคำขอรับของชิ้นนี้ไปแล้วหรือไม่
    user_claim = None
    if request.user.is_authenticated:
        user_claim = ClaimRequest.objects.filter(item=item, requester=request.user).first()

    # ดึงความคิดเห็นหลัก (parent=None) พร้อม prefetch replies และ profile
    comments = item.comments.filter(parent=None).select_related('author__profile').prefetch_related('replies__author__profile')
    total_comments_count = item.comments.count()

    context = {
        'item': item,
        'user_claim': user_claim,
        'comments': comments,
        'total_comments_count': total_comments_count,
    }
    return render(request, 'share/item_detail.html', context)


@login_required
def comment_create(request, item_id):
    """ส่งความคิดเห็นใหม่ หรือตอบกลับความคิดเห็น (Replies)"""
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')

        if not content:
            messages.error(request, "กรุณากรอกข้อความความคิดเห็น")
            return redirect('item_detail', pk=item.pk)

        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(pk=parent_id, item=item)
            except Comment.DoesNotExist:
                parent = None

        comment = Comment.objects.create(
            item=item,
            author=request.user,
            parent=parent,
            content=content
        )

        # ส่ง Notification แจ้งเตือน
        sender_name = request.user.first_name or request.user.username
        if parent:
            if parent.author != request.user:
                Notification.objects.create(
                    recipient=parent.author,
                    sender=request.user,
                    item=item,
                    comment=comment,
                    notification_type='reply_new',
                    title=f"{sender_name} ตอบกลับความคิดเห็นของคุณ",
                    message=f"{sender_name}: \"{content[:80]}\""
                )
        else:
            if item.owner != request.user:
                Notification.objects.create(
                    recipient=item.owner,
                    sender=request.user,
                    item=item,
                    comment=comment,
                    notification_type='comment_new',
                    title=f"{sender_name} แสดงความคิดเห็นบน '{item.title}'",
                    message=f"{sender_name}: \"{content[:80]}\""
                )

        messages.success(request, "ส่งความคิดเห็นเรียบร้อยแล้ว")
        return redirect(f"{reverse('item_detail', kwargs={'pk': item.pk})}#comment-{comment.pk}")

    return redirect('item_detail', pk=item.pk)


@login_required
def comment_delete(request, pk):
    """ลบความคิดเห็น (ผู้เขียนคอมเมนต์, เจ้าของประกาศ, หรือ Admin)"""
    comment = get_object_or_404(Comment, pk=pk)
    item_pk = comment.item.pk

    if comment.author == request.user or comment.item.owner == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, "ลบความคิดเห็นเรียบร้อยแล้ว")
    else:
        messages.error(request, "คุณไม่มีสิทธิ์ลบความคิดเห็นนี้")

    return redirect('item_detail', pk=item_pk)


@login_required
def item_create(request):
    """บันทึกสิ่งของใหม่ (ผูก owner = request.user)"""
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            messages.success(request, f"ลงประกาศ '{item.title}' สำเร็จแล้ว!")
            return redirect('item_detail', pk=item.pk)
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อผิดพลาด")
    else:
        form = ItemForm()

    return render(request, 'share/item_form.html', {
        'form': form,
        'action_title': 'ลงประกาศส่งต่อสิ่งของ',
        'is_edit': False
    })


@login_required
def item_edit(request, pk):
    """เจ้าของแก้ไขข้อมูลสิ่งของได้"""
    item = get_object_or_404(Item, pk=pk)

    # ตรวจสอบสิทธิ์ว่าเป็นเจ้าของประกาศหรือเป็น Admin หรือไม่
    if item.owner != request.user and not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์แก้ไขประกาศของผู้อื่น")
        return redirect('item_detail', pk=item.pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"แก้ไขข้อมูล '{item.title}' สำเร็จแล้ว!")
            return redirect('item_detail', pk=item.pk)
        else:
            messages.error(request, "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบข้อผิดพลาด")
    else:
        form = ItemForm(instance=item)

    return render(request, 'share/item_form.html', {
        'form': form,
        'item': item,
        'action_title': f'แก้ไขประกาศ: {item.title}',
        'is_edit': True
    })


@login_required
def item_delete(request, pk):
    """เจ้าของหรือ Admin ลบสิ่งของได้"""
    item = get_object_or_404(Item, pk=pk)

    if item.owner != request.user and not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์ลบประกาศของผู้อื่น")
        return redirect('item_detail', pk=item.pk)

    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f"ลบประกาศ '{title}' เรียบร้อยแล้ว")
        return redirect('my_items')

    return render(request, 'share/item_confirm_delete.html', {'item': item})


# ==========================================
# 3. Claim Request Views (การขอนัดรับของ & จัดการคำขอ)
# ==========================================

@login_required
def claim_create(request, item_id):
    """กรอกฟอร์มขอนัดรับของ"""
    item = get_object_or_404(Item, pk=item_id)

    # ห้ามเจ้าของขอรับของตัวเอง
    if item.owner == request.user:
        messages.warning(request, "คุณเป็นเจ้าของประกาศนี้ ไม่สามารถขอรับของตนเองได้")
        return redirect('item_detail', pk=item.pk)

    # ตรวจสอบว่าของยังว่างอยู่หรือไม่
    if item.status == 'completed':
        messages.warning(request, "ของชิ้นนี้ถูกส่งมอบสำเร็จไปแล้ว")
        return redirect('item_detail', pk=item.pk)

    # ตรวจสอบว่าเคยส่งคำขอไปแล้วหรือไม่
    existing_claim = ClaimRequest.objects.filter(item=item, requester=request.user).first()
    if existing_claim:
        messages.info(request, "คุณได้ส่งคำขอนัดรับของชิ้นนี้ไว้แล้ว")
        return redirect('item_detail', pk=item.pk)

    if request.method == 'POST':
        form = ClaimRequestForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.requester = request.user
            claim.save()

            # อัปเดตสถานะของเป็น 'reserved'
            if item.status == 'available':
                item.status = 'reserved'
                item.save()

            # แจ้งเตือนไปยังเจ้าของสิ่งของ
            Notification.objects.create(
                recipient=item.owner,
                sender=request.user,
                item=item,
                claim=claim,
                notification_type='claim_new',
                title=f'มีคำขอนัดรับใหม่: {item.title}',
                message=f'คุณ {request.user.first_name or request.user.username} ได้ส่งคำขอนัดรับ {item.title} ณ {claim.pickup_place}',
            )

            messages.success(request, f"ส่งคำขอนัดรับ '{item.title}' ถึงผู้ให้เรียบร้อยแล้ว!")
            return redirect('item_detail', pk=item.pk)
    else:
        form = ClaimRequestForm()

    return render(request, 'share/claim_form.html', {
        'form': form,
        'item': item,
    })


@login_required
def claim_confirm(request, claim_id):
    """เจ้าของหรือ Admin กดยืนยันการส่งมอบสำเร็จ"""
    claim = get_object_or_404(ClaimRequest, pk=claim_id)

    if claim.item.owner != request.user and not request.user.is_staff:
        messages.error(request, "คุณไม่ใช่เจ้าของสิ่งของนี้")
        return redirect('my_items')

    if request.method == 'POST':
        # สลับสถานะหรือยืนยัน
        claim.is_confirmed = not claim.is_confirmed
        claim.save()

        # อัปเดตสถานะของตามการยืนยัน
        if claim.is_confirmed:
            claim.item.status = 'completed'
            messages.success(request, f"ยืนยันการส่งมอบ '{claim.item.title}' สำเร็จแล้ว!")
            
            # แจ้งเตือนไปยังผู้ขอรับของ
            Notification.objects.create(
                recipient=claim.requester,
                sender=request.user,
                item=claim.item,
                claim=claim,
                notification_type='claim_confirmed',
                title=f'ยืนยันการส่งมอบ: {claim.item.title}',
                message=f'คุณ {request.user.first_name or request.user.username} ได้ยืนยันการส่งมอบ {claim.item.title} ให้คุณเรียบร้อยแล้ว',
            )
        else:
            claim.item.status = 'reserved'
            messages.info(request, f"ยกเลิกการยืนยันส่งมอบ '{claim.item.title}'")
        claim.item.save()

    return redirect('my_items')


@login_required
def my_items(request):
    """ดูรายการของที่ตัวเองลงประกาศไว้ และดูคำขอที่มีคนขอนัดรับ"""
    # ประกาศของฉัน
    my_published_items = Item.objects.filter(owner=request.user).order_by('-created_at')

    # คำขอรับของที่ส่งมาหาของของฉัน
    incoming_claims = ClaimRequest.objects.filter(item__owner=request.user).select_related('item', 'requester').order_by('-created_at')

    # คำขอรับของที่ฉันไปส่งไว้หาคนอื่น
    my_requests = ClaimRequest.objects.filter(requester=request.user).select_related('item', 'item__owner').order_by('-created_at')

    context = {
        'my_items': my_published_items,
        'incoming_claims': incoming_claims,
        'my_requests': my_requests,
    }
    return render(request, 'share/my_items.html', context)


# ==========================================
# 4. Extra: Dashboard & Chart.js สถิติแยกตามชั้นปี
# ==========================================

@login_required
def dashboard(request):
    """
    หน้าสถิติภาพรวมการส่งต่อของในระบบ (เฉพาะ Admin / Staff)
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "คุณไม่มีสิทธิ์เข้าถึงหน้าสถิติ (สำหรับผู้ดูแลระบบเท่านั้น)")
        return redirect('item_list')

    # สถิติตัวเลขภาพรวม
    total_items = Item.objects.count()
    available_items = Item.objects.filter(status='available').count()
    reserved_items = Item.objects.filter(status='reserved').count()
    completed_items = Item.objects.filter(status='completed').count()
    total_claims = ClaimRequest.objects.count()

    # สถิติของแจกฟรี vs จำหน่าย
    free_items_count = Item.objects.filter(price=0).count()
    paid_items_count = Item.objects.filter(price__gt=0).count()

    # รายการสิ่งของล่าสุดในระบบสำหรับตรวจสอบ
    recent_items = Item.objects.select_related('owner').order_by('-created_at')[:8]

    context = {
        # ข้อมูลการ์ดสถิติภาพรวม
        'total_items': total_items,
        'available_items': available_items,
        'reserved_items': reserved_items,
        'completed_items': completed_items,
        'total_claims': total_claims,
        'free_items_count': free_items_count,
        'paid_items_count': paid_items_count,

        # รายการล่าสุด
        'recent_items': recent_items,
    }
    return render(request, 'share/dashboard.html', context)


# ==========================================
# 4. Notification Views (ระบบแจ้งเตือน)
# ==========================================

@login_required
def mark_all_notifications_read(request):
    """ทำเครื่องหมายว่าอ่านแล้วสำหรับการแจ้งเตือนทั้งหมดของผู้ใช้"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({'status': 'ok', 'unread_count': 0})
    return redirect(request.META.get('HTTP_REFERER', 'item_list'))


@login_required
def mark_notification_read(request, pk):
    """ทำเครื่องหมายว่าอ่านแล้วสำหรับรายการเดียว แล้วนำทางไปยังหน้าที่เกี่ยวข้อง"""
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    
    if notif.comment and notif.item:
        return redirect(f"{reverse('item_detail', kwargs={'pk': notif.item.pk})}#comment-{notif.comment.pk}")
    if notif.claim:
        return redirect('my_requests')
    if notif.item:
        return redirect('item_detail', pk=notif.item.pk)
    return redirect('item_list')


# ==========================================
# 5. User Profile View (ข้อมูลส่วนตัว)
# ==========================================

@login_required
def profile_view(request):
    """แสดงและแก้ไขข้อมูลโปรไฟล์ส่วนตัวของผู้ใช้"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "บันทึกและอัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว!")
            return redirect('profile')
        else:
            messages.error(request, "กรุณาตรวจสอบข้อผิดพลาดในแบบฟอร์ม")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    # สถิติต่างๆ ของผู้ใช้
    my_items = Item.objects.filter(owner=request.user).order_by('-created_at')
    my_items_count = my_items.count()
    completed_items_count = my_items.filter(status='completed').count()
    my_claims_count = ClaimRequest.objects.filter(requester=request.user).count()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'my_items': my_items[:6],
        'my_items_count': my_items_count,
        'completed_items_count': completed_items_count,
        'my_claims_count': my_claims_count,
    }
    return render(request, 'share/profile.html', context)


# ==========================================
# 6. Settings View (การตั้งค่า & ธีม)
# ==========================================

@login_required
def settings_view(request):
    """หน้าตั้งค่าระบบ บัญชี ความเป็นส่วนตัว และเปลี่ยนธีม"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'theme_mode': profile.theme_mode, 'accent_color': profile.accent_color})
            messages.success(request, "บันทึกการตั้งค่าระบบเรียบร้อยแล้ว!")
            return redirect('settings')
        else:
            messages.error(request, "ไม่สามารถบันทึกการตั้งค่าได้ กรุณาลองใหม่อีกครั้ง")
    else:
        form = UserSettingsForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'share/settings.html', context)


@login_required
def update_theme_api(request):
    """API สำหรับเปลี่ยนธีมแบบ Real-time โดยไม่ต้องรีเฟรชหน้า"""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            theme_mode = data.get('theme_mode')
            accent_color = data.get('accent_color')

            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            if theme_mode:
                profile.theme_mode = theme_mode
            if accent_color:
                profile.accent_color = accent_color
            profile.save()

            return JsonResponse({'status': 'ok', 'theme_mode': profile.theme_mode, 'accent_color': profile.accent_color})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)
