from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Item, ClaimRequest, UserProfile

# Consistent clean modern input class
INPUT_BASE_CLASS = (
    'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 '
    'rounded-xl text-gray-800 placeholder-gray-400 '
    'focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 '
    'focus:outline-none transition text-sm'
)

FILE_INPUT_CLASS = (
    'w-full px-3 py-2 bg-gray-50 border border-gray-200 '
    'rounded-xl text-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none transition '
    'file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold '
    'file:bg-blue-50 file:text-blue-600 '
    'hover:file:bg-blue-100 cursor-pointer text-sm'
)


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150, 
        required=True, 
        label="ชื่อจริง",
        widget=forms.TextInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'ชื่อจริง'
        })
    )
    last_name = forms.CharField(
        max_length=150, 
        required=True, 
        label="นามสกุล",
        widget=forms.TextInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'นามสกุล'
        })
    )
    email = forms.EmailField(
        required=True, 
        label="อีเมล",
        widget=forms.EmailInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'student@university.ac.th'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['student_id', 'year_level', 'phone_number', 'line_id', 'bio', 'avatar']
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASS,
                'placeholder': 'เช่น 65014820'
            }),
            'year_level': forms.Select(attrs={
                'class': INPUT_BASE_CLASS
            }),
            'phone_number': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASS,
                'placeholder': 'เช่น 081-234-5678'
            }),
            'line_id': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASS,
                'placeholder': 'เช่น somchai.cs'
            }),
            'bio': forms.Textarea(attrs={
                'class': INPUT_BASE_CLASS,
                'rows': 3,
                'placeholder': 'แนะนำตัวสั้นๆ เช่น นักศึกษาสาขาวิทยาการคอมพิวเตอร์ ยินดีส่งต่อของดีสู่รุ่นน้อง'
            }),
            'avatar': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS
            }),
        }


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, 
        required=True, 
        label="ชื่อจริง",
        widget=forms.TextInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'ชื่อจริง'
        })
    )
    last_name = forms.CharField(
        max_length=150, 
        required=True, 
        label="นามสกุล",
        widget=forms.TextInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'นามสกุล'
        })
    )
    student_id = forms.CharField(
        max_length=20,
        required=True,
        label="รหัสนักศึกษา",
        widget=forms.TextInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'เช่น 65014820'
        })
    )
    year_level = forms.TypedChoiceField(
        choices=UserProfile.YEAR_LEVEL_CHOICES,
        coerce=int,
        initial=1,
        required=True,
        label="ชั้นปี",
        widget=forms.Select(attrs={
            'class': INPUT_BASE_CLASS
        })
    )
    email = forms.EmailField(
        required=True, 
        label="อีเมล",
        widget=forms.EmailInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'student@university.ac.th'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({
                'class': INPUT_BASE_CLASS,
                'placeholder': 'ชื่อผู้ใช้ (Username)'
            })
            self.fields['username'].label = "ชื่อผู้ใช้ (Username)"
        
        for field in self.fields.values():
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs.update({
                    'class': INPUT_BASE_CLASS,
                    'placeholder': '••••••••'
                })

    def save(self, commit=True):
        user = super().save(commit=commit)
        student_id = self.cleaned_data.get('student_id')
        year_level = self.cleaned_data.get('year_level')
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if student_id:
                profile.student_id = student_id
            if year_level:
                profile.year_level = year_level
            profile.save()
        return user


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'price', 'contact_link', 'image', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASS,
                'placeholder': 'ระบุชื่อสิ่งของที่ต้องการส่งต่อ'
            }),
            'price': forms.NumberInput(attrs={
                'class': INPUT_BASE_CLASS,
                'min': '0',
                'step': '1',
                'placeholder': '0.00 (ใส่ 0 เมื่อต้องการส่งต่อฟรี)'
            }),
            'contact_link': forms.TextInput(attrs={
                'class': INPUT_BASE_CLASS,
                'placeholder': 'เช่น https://line.me/ti/p/... หรือ ลิงก์ Facebook / Instagram'
            }),
            'image': forms.FileInput(attrs={
                'class': FILE_INPUT_CLASS
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_BASE_CLASS,
                'rows': 4,
                'placeholder': 'ระบุสภาพ ตำหนิ ข้อมูลของ หรือรายละเอียดที่ต้องการบอกผู้รับ'
            }),
        }


class ClaimRequestForm(forms.ModelForm):
    pickup_place = forms.ChoiceField(
        choices=ClaimRequest.PICKUP_CHOICES,
        widget=forms.RadioSelect,
        initial='ใต้ตึกคณะ ICT (ลานกิจกรรม)',
        label="จุดนัดรับที่สะดวก"
    )

    class Meta:
        model = ClaimRequest
        fields = ['pickup_place', 'meetup_date', 'note']
        widgets = {
            'meetup_date': forms.DateInput(attrs={
                'class': INPUT_BASE_CLASS,
                'type': 'date'
            }),
            'note': forms.Textarea(attrs={
                'class': INPUT_BASE_CLASS,
                'rows': 3,
                'placeholder': 'เช่น สะดวกช่วงเที่ยง 12:00-13:00 น. หรือทักไลน์มาได้เลยครับ'
            }),
        }


class ClaimConfirmForm(forms.ModelForm):
    class Meta:
        model = ClaimRequest
        fields = ['is_confirmed']
        widgets = {
            'is_confirmed': forms.CheckboxInput(attrs={
                'class': 'w-5 h-5 text-orange-600 rounded border-slate-300 dark:border-slate-600 dark:bg-slate-800 focus:ring-orange-500 cursor-pointer'
            })
        }


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['theme_mode', 'accent_color']
        widgets = {
            'theme_mode': forms.Select(attrs={
                'class': INPUT_BASE_CLASS
            }),
            'accent_color': forms.Select(attrs={
                'class': INPUT_BASE_CLASS
            }),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': INPUT_BASE_CLASS,
                'placeholder': '••••••••'
            })


class UserPasswordResetForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        label="ชื่อผู้ใช้ หรือ รหัสนักศึกษา",
        widget=forms.TextInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'ระบุชื่อผู้ใช้ เช่น somchai_ict'
        })
    )
    email = forms.EmailField(
        required=True,
        label="อีเมลที่ลงทะเบียน",
        widget=forms.EmailInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': 'เช่น somchai@university.ac.th'
        })
    )
    new_password1 = forms.CharField(
        label="รหัสผ่านใหม่",
        widget=forms.PasswordInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': '••••••••'
        })
    )
    new_password2 = forms.CharField(
        label="ยืนยันรหัสผ่านใหม่",
        widget=forms.PasswordInput(attrs={
            'class': INPUT_BASE_CLASS,
            'placeholder': '••••••••'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("รหัสผ่านใหม่ทั้งสองช่องไม่ตรงกัน")
        return cleaned_data

