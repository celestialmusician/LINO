import json
import random
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse

from .models import Product, Order, OrderItem, Review, Category, PasswordResetOTP, ChangePasswordOTP
from .forms import (
    UserRegisterForm, UserLoginForm, UserProfileForm, CheckoutForm, ContactForm, ReviewForm,
    ForgotPasswordForm, ResetPasswordConfirmForm, ChangePasswordForm, VerifyOTPForm
)
from .utils import generate_otp, send_otp_email


def initiate_razorpay_payment(order, total_amount):
    key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_lino_dummy')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'lino_dummy_secret')
    amount_in_paise = int(total_amount * 100)

    if key_id.startswith('rzp_test_lino_dummy') or not key_id:
        razorpay_order_id = f"order_dummy_{order.order_id}"
    else:
        try:
            client = razorpay.Client(auth=(key_id, key_secret))
            rzp_order = client.order.create({
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": order.order_id,
                "payment_capture": 1
            })
            razorpay_order_id = rzp_order['id']
        except Exception:
            razorpay_order_id = f"order_dummy_{order.order_id}"

    order.razorpay_order_id = razorpay_order_id
    order.save()

    return {
        "key_id": key_id,
        "amount": amount_in_paise,
        "currency": "INR",
        "razorpay_order_id": razorpay_order_id,
        "order_id": order.order_id,
    }


# ==================================================
# HOME
# ==================================================

class HomeView(View):

    def get(self, request, *args, **kwargs):

        featured_products = Product.objects.filter(
            is_active=True,
            featured=True
        ).order_by("-created_at")[:6]

        return render(
            request,
            "app/home.html",
            {
                "featured_products": featured_products,
            }
        )


# ==================================================
# COLLECTIONS
# ==================================================

class CollectionsView(View):

    def get(self, request, *args, **kwargs):

        category_slug = request.GET.get("category", "").strip()

        products = Product.objects.filter(is_active=True)

        if category_slug:
            products = products.filter(category__slug=category_slug)

        products = products.order_by("-created_at")
        categories = Category.objects.filter(is_active=True)

        return render(
            request,
            "app/collections.html",
            {
                "products": products,
                "categories": categories,
                "selected_category": category_slug,
            }
        )


# ==================================================
# STORY
# ==================================================

class StoryView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "app/story.html")


# ==================================================
# CONTACT
# ==================================================

class ContactView(View):

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, "app/contact.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Thank you for contacting LINO! We will get back to you shortly.")
            return redirect("contact")
        return render(request, "app/contact.html", {"form": form})


# ==================================================
# PRODUCT DETAIL & REVIEWS
# ==================================================

class ProductDetailView(View):

    def get(self, request, slug, *args, **kwargs):

        product = get_object_or_404(Product, slug=slug, is_active=True)

        reviews = product.reviews.filter(is_approved=True)

        related_products = Product.objects.filter(
            is_active=True
        ).exclude(slug=slug).order_by("?")[:4]

        review_form = ReviewForm()

        return render(
            request,
            "app/product-detail.html",
            {
                "product": product,
                "reviews": reviews,
                "review_form": review_form,
                "related_products": related_products,
            }
        )


class AddReviewView(View):

    def post(self, request, slug, *args, **kwargs):

        product = get_object_or_404(Product, slug=slug, is_active=True)

        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product

            if request.user.is_authenticated:
                review.user = request.user
                # Check if user has purchased this product
                has_purchased = OrderItem.objects.filter(
                    order__user=request.user,
                    product=product
                ).exists()
                review.verified_purchase = has_purchased

            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
        else:
            messages.error(request, "Please correct the errors in your review form.")

        return redirect("product-detail", slug=slug)


# ==================================================
# WISHLIST & CART
# ==================================================

class WishlistView(View):

    def get(self, request):
        return render(request, "app/wishlist.html")


class CartView(View):

    template_name = "app/cart.html"

    def get(self, request):
        return render(request, self.template_name)


# ==================================================
# CHECKOUT (ATOMIC & SECURE PRICE VERIFICATION)
# ==================================================

class CheckoutView(View):

    template_name = "app/checkout.html"

    def get(self, request):

        initial = {}
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            initial = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': profile.phone if profile else '',
                'address': profile.address if profile else '',
                'city': profile.city if profile else '',
                'state': profile.state if profile else '',
                'pincode': profile.pincode if profile else '',
            }

        form = CheckoutForm(initial=initial)
        razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_lino_dummy')
        return render(request, self.template_name, {
            "form": form,
            "razorpay_key_id": razorpay_key_id,
            "require_auth": not request.user.is_authenticated
        })

    def post(self, request):
        if not request.user.is_authenticated:
            is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"
            if is_ajax:
                return JsonResponse({"status": "REQUIRE_AUTH", "message": "Please sign in or create an account to place your order."}, status=401)
            messages.error(request, "Please sign in or create an account to place your order.")
            return redirect(f"{reverse('login')}?next={reverse('checkout')}")

        form = CheckoutForm(request.POST)
        cart_json = request.POST.get("cart_data", "[]")

        try:
            cart_items = json.loads(cart_json)
        except (json.JSONDecodeError, TypeError):
            cart_items = []

        if not cart_items:
            messages.error(request, "Your cart is empty. Please add items to checkout.")
            return render(request, self.template_name, {"form": form})

        if not form.is_valid():
            messages.error(request, "Please check your shipping and billing details for errors.")
            return render(request, self.template_name, {"form": form})

        # Atomic transaction: Create Order + OrderItems + Recalculate Prices + Decrement Stock
        try:
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                    profile = getattr(request.user, 'profile', None)
                    if profile:
                        if order.phone: profile.phone = order.phone
                        if order.address: profile.address = order.address
                        if order.city: profile.city = order.city
                        if order.state: profile.state = order.state
                        if order.pincode: profile.pincode = order.pincode
                        profile.save()
                order.total = 0  # Will be calculated securely on server
                order.save()

                total_amount = 0
                order_items_to_create = []

                for item in cart_items:
                    slug = item.get("slug", "")
                    qty = int(item.get("quantity", 1))

                    if qty <= 0:
                        continue

                    # Server-side price lookup (Defeats price tampering)
                    try:
                        product = Product.objects.select_for_update().get(slug=slug, is_active=True)
                    except Product.DoesNotExist:
                        continue

                    # Check stock availability
                    if product.stock > 0 and product.stock >= qty:
                        product.stock -= qty
                        product.save()

                    price = product.price
                    subtotal = price * qty
                    total_amount += subtotal

                    order_items_to_create.append(
                        OrderItem(
                            order=order,
                            product=product,
                            quantity=qty,
                            price_at_order=price
                        )
                    )

                if not order_items_to_create:
                    raise ValueError("No valid products found in cart.")

                OrderItem.objects.bulk_create(order_items_to_create)

                # Save true server-calculated total
                order.total = total_amount
                order.save()

            is_online_payment = (order.payment_method in ['upi', 'card', 'razorpay', 'online']) or request.POST.get("is_online_payment") == "true"
            is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"

            if is_online_payment:
                # Prefer creating a Razorpay hosted payment link when enabled
                use_payment_link = getattr(settings, 'RAZORPAY_USE_PAYMENT_LINK', False)
                if use_payment_link:
                    key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_lino_dummy')
                    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'lino_dummy_secret')
                    amount_in_paise = int(total_amount * 100)
                    payment_link_url = None
                    if not key_id.startswith('rzp_test_lino_dummy') and key_id and key_secret:
                        try:
                            client = razorpay.Client(auth=(key_id, key_secret))
                            pl = client.payment_link.create({
                                "amount": amount_in_paise,
                                "currency": "INR",
                                "reference_id": order.order_id,
                                "description": f"Order #{order.order_id}",
                                "customer": {
                                    "name": f"{order.first_name} {order.last_name}",
                                    "email": order.email,
                                    "contact": order.phone
                                },
                                "notify": {"sms": False, "email": False},
                                "reminder_enable": False,
                                "notes": {"order_id": order.order_id},
                                "callback_url": request.build_absolute_uri(reverse('razorpay_verify')),
                                "callback_method": "get"
                            })
                            payment_link_url = pl.get('short_url') or pl.get('long_url') or pl.get('url')
                        except Exception:
                            payment_link_url = None

                    if is_ajax:
                        if payment_link_url:
                            return JsonResponse({
                                "status": "RAZORPAY_LINK",
                                "payment_link_url": payment_link_url
                            })

                # Dedicated Razorpay Payment Page Flow
                rzp_data = initiate_razorpay_payment(order, total_amount)
                payment_page_url = reverse("razorpay_page", kwargs={"order_id": order.order_id})
                if is_ajax:
                    return JsonResponse({
                        "status": "RAZORPAY_INIT",
                        "redirect_url": payment_page_url,
                        "payment_page_url": payment_page_url,
                        "razorpay_key_id": rzp_data["key_id"],
                        "razorpay_order_id": rzp_data["razorpay_order_id"],
                        "amount": rzp_data["amount"],
                        "currency": "INR",
                        "order_id": order.order_id,
                        "name": f"{order.first_name} {order.last_name}",
                        "email": order.email,
                        "phone": order.phone,
                    })
                return redirect(payment_page_url)

            messages.success(request, f"Order {order.order_id} placed successfully!")
            if is_ajax:
                return JsonResponse({"status": "SUCCESS", "redirect_url": reverse("order_success")})
            return redirect("order_success")

        except Exception as e:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "ERROR", "message": str(e)}, status=400)
            messages.error(request, f"An error occurred while processing your order: {str(e)}")
            return render(request, self.template_name, {"form": form})


# ==================================================
# RAZORPAY PAYMENT VERIFICATION
# ==================================================

@method_decorator(csrf_exempt, name='dispatch')
class RazorpayVerifyView(View):

    def post(self, request):
        data = request.POST
        razorpay_order_id = data.get("razorpay_order_id", "")
        razorpay_payment_id = data.get("razorpay_payment_id", "")
        razorpay_signature = data.get("razorpay_signature", "")

        if not razorpay_order_id and request.body:
            try:
                json_data = json.loads(request.body.decode("utf-8"))
                razorpay_order_id = json_data.get("razorpay_order_id", "")
                razorpay_payment_id = json_data.get("razorpay_payment_id", "")
                razorpay_signature = json_data.get("razorpay_signature", "")
            except Exception:
                pass

        if not razorpay_order_id:
            return JsonResponse({"status": "ERROR", "message": "Missing Razorpay order ID"}, status=400)

        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return JsonResponse({"status": "ERROR", "message": "Order not found"}, status=404)

        key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_lino_dummy')
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'lino_dummy_secret')

        verified = False

        if key_id.startswith('rzp_test_lino_dummy') or razorpay_order_id.startswith('order_dummy_') or not key_secret:
            # Test / Dummy mode auto-verify
            verified = True
        else:
            try:
                client = razorpay.Client(auth=(key_id, key_secret))
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
                verified = True
            except Exception:
                verified = False

        if verified:
            order.razorpay_payment_id = razorpay_payment_id or f"pay_dummy_{order.order_id}"
            order.razorpay_signature = razorpay_signature or "dummy_signature_ok"
            order.is_paid = True
            order.status = "confirmed"
            order.save()
            return JsonResponse({
                "status": "SUCCESS",
                "message": "Payment verified successfully!",
                "redirect_url": reverse("order_success")
            })
        else:
            return JsonResponse({"status": "ERROR", "message": "Payment signature verification failed"}, status=400)


# ==================================================
# DEDICATED RAZORPAY PAYMENT PAGE
# ==================================================

class RazorpayPageView(View):

    template_name = "app/razorpay_page.html"

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)

        # If order is already paid, redirect directly to order success
        if order.is_paid:
            messages.info(request, f"Order #{order.order_id} is already paid!")
            return redirect("order_success")

        # Ensure Razorpay order ID is generated and saved on the Order object
        if not order.razorpay_order_id:
            rzp_data = initiate_razorpay_payment(order, order.total)
            razorpay_order_id = rzp_data["razorpay_order_id"]
        else:
            razorpay_order_id = order.razorpay_order_id

        razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_lino_dummy')
        amount_in_paise = int(order.total * 100)

        context = {
            "order": order,
            "order_items": order.items.select_related('product').all(),
            "razorpay_key_id": razorpay_key_id,
            "razorpay_order_id": razorpay_order_id,
            "amount_in_paise": amount_in_paise,
            "total_amount": order.total,
            "currency": "INR",
        }
        return render(request, self.template_name, context)


# ==================================================
# ORDER SUCCESS
# ==================================================

class OrderSuccessView(View):

    template_name = "app/order-success.html"

    def get(self, request):
        return render(request, self.template_name)


# ==================================================
# USER PROFILE & MY ORDERS
# ==================================================

class ProfileView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        phone = ""
        if hasattr(request.user, 'profile'):
            phone = request.user.profile.phone

        form = UserProfileForm(initial={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': phone,
        })
        return render(
            request,
            "app/profile.html",
            {
                "orders": orders,
                "order_count": orders.count(),
                "form": form,
            }
        )

    def post(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        form = UserProfileForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email'].strip().lower()
            phone = form.cleaned_data.get('phone', '').strip()

            name_parts = full_name.split(" ", 1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
            request.user.email = email
            request.user.save()

            if hasattr(request.user, 'profile'):
                request.user.profile.phone = phone
                request.user.profile.save()

            messages.success(request, "Your profile details have been updated successfully.")
            return redirect("profile")

        return render(
            request,
            "app/profile.html",
            {
                "orders": orders,
                "order_count": orders.count(),
                "form": form,
            }
        )


class MyOrdersView(LoginRequiredMixin, View):

    login_url = "/login/"

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related("items__product").order_by("-created_at")

        return render(request, "app/my_orders.html", {"orders": orders})


# ==================================================
# AUTHENTICATION (LOGIN, REGISTER, LOGOUT)
# ==================================================

class LoginView(View):

    template_name = "app/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = UserLoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email_input = form.cleaned_data['email'].strip()
            password = form.cleaned_data['password']

            # Case-insensitive lookup by email or username
            user_obj = User.objects.filter(email__iexact=email_input).first()
            if not user_obj:
                user_obj = User.objects.filter(username__iexact=email_input).first()

            if not user_obj:
                msg = "No account found with this email address."
                if is_ajax:
                    return JsonResponse({"status": "ERROR", "message": msg}, status=400)
                messages.error(request, msg)
                return render(request, self.template_name, {"form": form})

            # Authenticate using user_obj.username, fallback to email if necessary
            user = authenticate(request, username=user_obj.username, password=password)
            if user is None and user_obj.email:
                user = authenticate(request, username=user_obj.email, password=password)
            if user is None:
                user = authenticate(request, username=email_input, password=password)

            if user is not None:
                login(request, user)
                next_url = request.POST.get("next") or request.GET.get("next") or reverse("checkout")
                if is_ajax:
                    return JsonResponse({
                        "status": "SUCCESS",
                        "message": f"Welcome back, {user.first_name or user.username}!",
                        "redirect": next_url,
                        "user": {
                            "first_name": user.first_name or user.username,
                            "email": user.email
                        }
                    })
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                msg = "Incorrect password. Please try again."
                if is_ajax:
                    return JsonResponse({"status": "ERROR", "message": msg}, status=400)
                messages.error(request, msg)
        else:
            errors = []
            for field, errs in form.errors.items():
                errors.extend(errs)
            msg = " ".join(errors) or "Invalid email or password."
            if is_ajax:
                return JsonResponse({"status": "ERROR", "message": msg}, status=400)

        return render(request, self.template_name, {"form": form})


class RegisterView(View):

    template_name = "app/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = UserRegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']

            name_parts = full_name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            username = email[:150]
            base_username = username
            counter = 1
            while User.objects.filter(username__iexact=username).exists():
                username = f"{base_username[:140]}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            phone = form.cleaned_data.get('phone', '').strip()
            if phone and hasattr(user, 'profile'):
                user.profile.phone = phone
                user.profile.save()

            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next") or reverse("checkout")
            if is_ajax:
                return JsonResponse({
                    "status": "SUCCESS",
                    "message": f"Welcome to LINO, {first_name}!",
                    "redirect": next_url,
                    "user": {
                        "first_name": first_name,
                        "email": email
                    }
                })
            messages.success(request, f"Welcome to LINO, {first_name}!")
            return redirect(next_url)
        else:
            errors = []
            for field, errs in form.errors.items():
                errors.extend(errs)
            msg = " ".join(errors) or "Please check registration details."
            if is_ajax:
                return JsonResponse({"status": "ERROR", "message": msg}, status=400)

        return render(request, self.template_name, {"form": form})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect("home")


# ==================================================
# FORGOT & LIVE OTP PASSWORD RESET VIEWS
# ==================================================

class ForgotPasswordView(View):
    template_name = "app/forgot_password.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        form = ForgotPasswordForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            user = User.objects.filter(email__iexact=email).first()

            if user:
                # OTP verification disabled (live): skip email/OTP step entirely
                # and let the user set a new password immediately.
                request.session['reset_email'] = email
                request.session['otp_verified_user_id'] = user.id

                messages.success(request, "Please enter your new password.")
                return redirect("set_new_password")

            messages.error(request, "No registered account was found with that email address.")
            return render(request, self.template_name, {"form": form})

        return render(request, self.template_name, {"form": form})


class VerifyOTPView(View):
    template_name = "app/verify_otp.html"

    def get(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Please enter your email to request a password reset OTP.")
            return redirect("forgot_password")
        form = VerifyOTPForm()
        latest_otp = request.session.get('latest_otp') if getattr(settings, "SHOW_TEST_OTP", False) else None
        return render(request, self.template_name, {
            "form": form,
            "email": email,
            "latest_otp": latest_otp,
        })

    def post(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Session expired. Please request a new OTP.")
            return redirect("forgot_password")

        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp_code']
            user = User.objects.filter(email__iexact=email).first()

            if user:
                valid_otps = PasswordResetOTP.objects.filter(
                    user=user,
                    otp_code=otp_entered,
                    is_used=False
                ).order_by('-created_at')
                
                # Check if valid
                matching_otp = None
                for otp_obj in valid_otps:
                    if otp_obj.is_valid():
                        matching_otp = otp_obj
                        break

                if matching_otp:
                    matching_otp.is_used = True
                    matching_otp.save()
                    request.session['otp_verified_user_id'] = user.id
                    messages.success(request, "OTP verified successfully! Please enter your new password.")
                    return redirect("set_new_password")
                else:
                    messages.error(request, "Invalid or expired OTP code. Please check and try again.")
            else:
                messages.error(request, "Account not found. Please restart the reset process.")
                return redirect("forgot_password")

        latest_otp = request.session.get('latest_otp') if getattr(settings, "SHOW_TEST_OTP", False) else None
        return render(request, self.template_name, {
            "form": form,
            "email": email,
            "latest_otp": latest_otp,
        })


class ResendOTPView(View):

    def get(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Session expired. Please request a new OTP.")
            return redirect("forgot_password")

        user = User.objects.filter(email__iexact=email).first()
        if user:
            otp_code = generate_otp()
            PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
            PasswordResetOTP.objects.create(user=user, otp_code=otp_code)

            email_sent = send_otp_email(user, otp_code, purpose="password_reset")
            if not getattr(settings, "SHOW_TEST_OTP", False):
                request.session.pop('latest_otp', None)
            else:
                request.session['latest_otp'] = otp_code

            if email_sent:
                messages.success(request, f"A new 6-digit OTP code has been sent to {email}. Check your inbox and Spam folder.")
            else:
                messages.error(request, f"Failed to send OTP email to {email}. Please try again later.")
        else:
            messages.error(request, "User not found.")

        return redirect("verify_otp")


class SetNewPasswordView(View):
    template_name = "app/reset_password_confirm.html"

    def get(self, request):
        user_id = request.session.get('otp_verified_user_id')
        if not user_id:
            messages.error(request, "OTP verification required first.")
            return redirect("forgot_password")

        form = ResetPasswordConfirmForm()
        return render(request, self.template_name, {"form": form, "validlink": True})

    def post(self, request):
        user_id = request.session.get('otp_verified_user_id')
        if not user_id:
            messages.error(request, "Session expired. Please restart password reset.")
            return redirect("forgot_password")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("forgot_password")

        form = ResetPasswordConfirmForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()

            # Clean up session keys
            request.session.pop('reset_email', None)
            request.session.pop('latest_otp', None)
            request.session.pop('otp_verified_user_id', None)

            messages.success(request, "Your password has been successfully updated! Please sign in with your new password.")
            return redirect("login")

        return render(request, self.template_name, {"form": form, "validlink": True})


class ResetPasswordConfirmView(View):
    template_name = "app/reset_password_confirm.html"

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = ResetPasswordConfirmForm()
            return render(request, self.template_name, {"form": form, "validlink": True})
        else:
            return render(request, self.template_name, {"validlink": False})

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = ResetPasswordConfirmForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been successfully reset! You can now sign in with your new password.")
                return redirect("login")
            return render(request, self.template_name, {"form": form, "validlink": True})
        else:
            return render(request, self.template_name, {"validlink": False})


class ChangePasswordView(LoginRequiredMixin, View):
    """
    Validates current password and applies the new password immediately.
    (OTP email-verification step removed for live use.)
    """
    login_url = "/login/"

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            # OTP verification disabled (live): apply the new password
            # immediately instead of emailing an OTP first.
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)

            messages.success(request, "Your password has been changed successfully!")
            return redirect("profile")

        # Form invalid — return to profile with errors
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        profile_form = UserProfileForm(initial={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        })
        return render(
            request,
            "app/profile.html",
            {
                "orders": orders,
                "order_count": orders.count(),
                "form": profile_form,
                "password_form": form,
            }
        )


# ==================================================
# VERIFY CHANGE PASSWORD OTP (Step 2)
# ==================================================

class VerifyChangePasswordOTPView(LoginRequiredMixin, View):
    """
    Step 2: User enters OTP to confirm password change.
    """
    login_url  = "/login/"
    template_name = "app/verify_change_password_otp.html"

    def get(self, request):
        if not request.session.get('change_pw_new_hash'):
            messages.error(request, "Please fill in the change password form first.")
            return redirect("profile")
        return render(request, self.template_name, {
            "email": request.user.email,
        })

    def post(self, request):
        otp_entered  = request.POST.get("otp_code", "").strip()
        new_pw_hash  = request.session.get('change_pw_new_hash')

        if not new_pw_hash:
            messages.error(request, "Session expired. Please try again.")
            return redirect("profile")

        # Verify OTP from DB
        valid_otp = ChangePasswordOTP.objects.filter(
            user=request.user,
            otp_code=otp_entered,
            is_used=False,
        ).order_by('-created_at').first()

        if valid_otp and valid_otp.is_valid():
            valid_otp.is_used = True
            valid_otp.save()

            # Apply the pre-validated password directly
            request.user.password = new_pw_hash
            request.user.save()
            update_session_auth_hash(request, request.user)

            # Clear session keys
            request.session.pop('change_pw_new_hash', None)
            request.session.pop('change_pw_otp', None)

            messages.success(request, "Your password has been changed successfully!")
            return redirect("profile")

        messages.error(request, "Invalid or expired OTP. Please try again.")
        return render(request, self.template_name, {
            "email": request.user.email,
        })

    def _handle_resend(self, request):
        otp_code = generate_otp()
        ChangePasswordOTP.objects.filter(user=request.user, is_used=False).update(is_used=True)
        ChangePasswordOTP.objects.create(user=request.user, otp_code=otp_code)
        email_sent = send_otp_email(request.user, otp_code, purpose="change_password")
        request.session.pop('change_pw_otp', None)
        if email_sent:
            messages.success(request, "A new OTP has been sent to your email.")
        else:
            messages.error(request, "Failed to send OTP email. Please try again.")
        return redirect("verify_change_password_otp")


# ==================================================
# RESEND CHANGE PASSWORD OTP
# ==================================================

class ResendChangePasswordOTPView(LoginRequiredMixin, View):
    """Resend OTP for the change-password flow (GET request)."""
    login_url = "/login/"

    def get(self, request):
        if not request.session.get('change_pw_new_hash'):
            messages.error(request, "Please fill in the change password form first.")
            return redirect("profile")

        otp_code = generate_otp()
        ChangePasswordOTP.objects.filter(user=request.user, is_used=False).update(is_used=True)
        ChangePasswordOTP.objects.create(user=request.user, otp_code=otp_code)

        email_sent = send_otp_email(request.user, otp_code, purpose="change_password")
        request.session.pop('change_pw_otp', None)
        if email_sent:
            messages.success(request, f"A new OTP code has been sent to {request.user.email}.")
        else:
            messages.error(request, f"Failed to send OTP email to {request.user.email}. Please try again.")

        return redirect("verify_change_password_otp")