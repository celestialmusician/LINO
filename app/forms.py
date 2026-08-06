import re
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Order, Review


# ==================================================
# USER REGISTER FORM
# ==================================================

class UserRegisterForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name',
            'required': True,
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'required': True,
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Mobile Number (e.g. 9876543210)',
        })
    )

    password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password (min 8 characters)',
            'required': True,
        })
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'required': True,
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            digits = re.sub(r'\D', '', phone)
            if len(digits) < 10 or len(digits) > 12:
                raise ValidationError("Please enter a valid mobile number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


# ==================================================
# USER LOGIN FORM
# ==================================================

class UserLoginForm(forms.Form):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'required': True,
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'required': True,
        })
    )


# ==================================================
# USER PROFILE FORM
# ==================================================

class UserProfileForm(forms.Form):

    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Full Name',
            'required': True,
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address',
            'required': True,
        })
    )

    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Mobile Number',
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            digits = re.sub(r'\D', '', phone)
            if len(digits) < 10 or len(digits) > 12:
                raise ValidationError("Please enter a valid mobile number.")
        return phone


# ==================================================
# CHECKOUT FORM
# ==================================================

class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'city',
            'state',
            'pincode',
            'payment_method',
            'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'required': True}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'required': True}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number', 'required': True}),
            'address': forms.Textarea(attrs={'placeholder': 'Complete Shipping Address', 'rows': 4, 'required': True}),
            'city': forms.TextInput(attrs={'placeholder': 'City', 'required': True}),
            'state': forms.TextInput(attrs={'placeholder': 'State', 'required': True}),
            'pincode': forms.TextInput(attrs={'placeholder': 'PIN Code (6 digits)', 'required': True}),
            'payment_method': forms.Select(attrs={'required': True}),
            'notes': forms.Textarea(attrs={'placeholder': 'Delivery Notes (Optional)', 'rows': 2}),
        }

    def clean_payment_method(self):
        method = self.cleaned_data.get('payment_method', '').strip()
        if not method or method not in ['cod', 'upi', 'card']:
            raise ValidationError("Please select a valid payment method.")
        return method

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode', '').strip()
        digits = re.sub(r'\D', '', pincode)
        if len(digits) != 6:
            raise ValidationError("Please enter a valid 6-digit Indian PIN code.")
        return digits

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10 or len(digits) > 12:
            raise ValidationError("Please enter a valid phone number.")
        return phone


# ==================================================
# CONTACT FORM
# ==================================================

class ContactForm(forms.Form):

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'required': True})
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'required': True})
    )

    subject = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Subject'})
    )

    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 5, 'required': True})
    )


# ==================================================
# REVIEW FORM
# ==================================================

class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['reviewer_name', 'reviewer_email', 'rating', 'headline', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'placeholder': 'Your Name', 'required': True}),
            'reviewer_email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'required': True}),
            'rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(5, 0, -1)]),
            'headline': forms.TextInput(attrs={'placeholder': 'Review Title (e.g. Magnificent scent)'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Share your experience with this perfume...', 'rows': 4, 'required': True}),
        }


# ==================================================
# FORGOT PASSWORD FORM
# ==================================================

class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your registered email address',
            'required': True,
        })
    )


# ==================================================
# VERIFY OTP FORM
# ==================================================

class VerifyOTPForm(forms.Form):

    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit OTP',
            'required': True,
            'maxlength': '6',
            'autocomplete': 'off',
            'pattern': '[0-9]{6}',
        })
    )

    def clean_otp_code(self):
        otp = self.cleaned_data.get('otp_code', '').strip()
        if not otp.isdigit() or len(otp) != 6:
            raise ValidationError("Please enter a valid 6-digit numeric OTP.")
        return otp


# ==================================================
# RESET PASSWORD CONFIRM FORM
# ==================================================

class ResetPasswordConfirmForm(forms.Form):

    new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password (min 8 characters)',
            'required': True,
        })
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'required': True,
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned_data


# ==================================================
# CHANGE PASSWORD FORM (LOGGED-IN USER)
# ==================================================

class ChangePasswordForm(forms.Form):

    old_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Current Password',
            'required': True,
        })
    )

    new_password = forms.CharField(
        min_length=8,
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password (min 8 characters)',
            'required': True,
        })
    )

    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm New Password',
            'required': True,
        })
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_pass = self.cleaned_data.get('old_password')
        if self.user and not self.user.check_password(old_pass):
            raise ValidationError("Incorrect current password.")
        return old_pass

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')

        if new_pass and confirm and new_pass != confirm:
            self.add_error('confirm_password', "New passwords do not match.")

        return cleaned_data
