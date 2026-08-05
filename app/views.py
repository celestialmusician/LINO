import json
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse

from .models import Product, Order, OrderItem, Review, Category
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm, CheckoutForm, ContactForm, ReviewForm


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
            initial = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
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

            is_online_payment = (order.payment_method in ['upi', 'card']) or request.POST.get("is_online_payment") == "true"
            is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"

            if is_online_payment:
                rzp_data = initiate_razorpay_payment(order, total_amount)
                if is_ajax:
                    return JsonResponse({
                        "status": "RAZORPAY_INIT",
                        "razorpay_key_id": rzp_data["key_id"],
                        "razorpay_order_id": rzp_data["razorpay_order_id"],
                        "amount": rzp_data["amount"],
                        "currency": "INR",
                        "order_id": order.order_id,
                        "name": f"{order.first_name} {order.last_name}",
                        "email": order.email,
                        "phone": order.phone,
                    })

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
        form = UserProfileForm(initial={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
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
            email = form.cleaned_data['email']

            name_parts = full_name.split(" ", 1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
            request.user.email = email
            request.user.save()

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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                msg = "No account found with this email address."
                if is_ajax:
                    return JsonResponse({"status": "ERROR", "message": msg}, status=400)
                messages.error(request, msg)
                return render(request, self.template_name, {"form": form})

            user = authenticate(request, username=username, password=password)

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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            name_parts = full_name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            username = email[:150]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

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