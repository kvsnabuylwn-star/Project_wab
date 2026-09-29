import os
import sys
import django

# Set UTF-8 encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from share.models import Item, ClaimRequest
from datetime import date, timedelta

def run_seed():
    print("--- เริ่มต้น Seeding ข้อมูลระบบ Major Share ---")

    # 1. สร้างผู้ใช้สำหรับทดสอบ
    u1, created = User.objects.get_or_create(username='senior_dev')
    if created:
        u1.set_password('password123')
        u1.first_name = 'รุ่นพี่'
        u1.last_name = 'ใจดี'
        u1.email = 'senior@major.ac.th'
        u1.is_staff = True
        u1.is_superuser = True
        u1.save()
        print(f"สร้าง User: {u1.username} (รหัสผ่าน: password123)")

    u2, created = User.objects.get_or_create(username='student_somchai')
    if created:
        u2.set_password('password123')
        u2.first_name = 'สมชาย'
        u2.last_name = 'รักเรียน'
        u2.email = 'somchai@major.ac.th'
        u2.save()
        print(f"สร้าง User: {u2.username} (รหัสผ่าน: password123)")

    # 2. สร้างสิ่งของและชีทสรุปตัวอย่าง
    items_data = [
        {
            'owner': u1,
            'title': 'ชีทสรุปวิชา Data Structures & Algorithm ลายมืออ่านง่าย พร้อมตัวอย่างโค้ด',
            'price': 0,
            'description': 'สรุปเนื้อหาตั้งแต่ Array, LinkedList, Stack, Queue, Tree จนถึง Graph พร้อมเทคนิคการไล่ Trace ตารางและคำนวณ Big O มีรอยไฮไลท์ช่วยจำ เหมาะสำหรับเตรียมสอบ Midterm/Final',
            'status': 'available'
        },
        {
            'owner': u1,
            'title': 'หนังสือการเขียนโปรแกรมเว็บด้วย Django & Python ฉบับภาษาไทย',
            'price': 120.00,
            'description': 'สภาพ 90% เนื้อหาละเอียดมาก มีตัวอย่างการทำ Authentication, ModelForm และ Templates เหมาะกับคนที่เรียนวิชา Web Dev เทอมนี้',
            'status': 'available'
        },
        {
            'owner': u1,
            'title': 'บอร์ด Arduino Uno R3 พร้อมกล่องอุปกรณ์สายไฟและเซนเซอร์แล็บ',
            'price': 0,
            'description': 'ส่งต่อบอร์ด Arduino ใช้เรียนตอนปี 2 เทอมก่อน ใช้งานได้ปกติ 100% มี Breadboard และสาย Jumper ครบเซ็ต',
            'status': 'reserved'
        },
        {
            'owner': u2,
            'title': 'ชีทสรุปแนวข้อสอบแคลคูลัส 1 พร้อมเฉลยวิธีทำข้อต่อข้อ',
            'price': 0,
            'description': 'รวบรวมโจทย์อนุพันธ์ อินทิกรัล และลิมิต 5 ปีย้อนหลัง มีวิธีทำละเอียดทุกขั้นตอน แจกฟรีให้น้องปี 1 นำไปติวสอบได้เลย',
            'status': 'available'
        },
        {
            'owner': u1,
            'title': 'คู่มือแนวทางการเตรียมหัวข้อ Senior Project และแม่แบบเอกสาร',
            'price': 0,
            'description': 'รวบรวมเทมเพลต Proposal และสไลด์พรีเซนต์โปรเจกต์จบที่ผ่านการตรวจจากอาจารย์แล้ว เหมาะกับรุ่นน้องปี 4 ที่กำลังเริ่มต้นทำโครงงาน',
            'status': 'completed'
        },
        {
            'owner': u2,
            'title': 'เสื้อกาวน์แล็บคอมพิวเตอร์ / เสื้อช็อปสาขา ไซส์ L',
            'price': 50.00,
            'description': 'เสื้อช็อปสภาพดี ซักรีดเรียบร้อย ไม่มีรอยเปื้อน ขนาดไซส์ L ส่งต่อให้เพื่อนในสาขาที่ต้องการใช้งาน',
            'status': 'available'
        }
    ]

    item_objs = []
    for idata in items_data:
        item, created = Item.objects.get_or_create(
            title=idata['title'],
            defaults=idata
        )
        item_objs.append(item)
    print(f"สร้างสิ่งของ/ชีทสรุปตัวอย่างจำนวน {len(item_objs)} รายการ")

    # 4. สร้างคำขอนัดรับของตัวอย่าง
    # ให้สมชายขอรับของชิ้นที่ 3 (Arduino) จากรุ่นพี่
    arduino_item = item_objs[2]
    claim, c_created = ClaimRequest.objects.get_or_create(
        item=arduino_item,
        requester=u2,
        defaults={
            'pickup_place': 'โต๊ะม้าหินอ่อนใต้ตึกสาขา หน้าห้องแล็บ 402',
            'meetup_date': date.today() + timedelta(days=2),
            'note': 'สะดวกช่วงพักเที่ยง 12:00-13:00 น. ครับพี่ ขอบคุณมากครับ',
            'is_confirmed': False
        }
    )
    if c_created:
        print(f"สร้างคำขอนัดรับตัวอย่าง: {claim}")

    print("--- เสร็จสิ้นการ Seeding ข้อมูลเรียบร้อย พร้อมใช้งานทันที! ---")

if __name__ == '__main__':
    run_seed()
