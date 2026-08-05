from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.HomeView.as_view(),
        name='home'
    ),

    path(
        'collections/',
        views.CollectionsView.as_view(),
        name='collections'
    ),

    path(
        "story/",
        views.StoryView.as_view(),
        name="story",
    ),

    path(
        'contact/',
        views.ContactView.as_view(),
        name='contact'
    ),

    path(
        'product/<slug:slug>/',
        views.ProductDetailView.as_view(),
        name='product-detail'
    ),

    path(
        'product/<slug:slug>/add-review/',
        views.AddReviewView.as_view(),
        name='add-review'
    ),

    path(
        "wishlist/",
        views.WishlistView.as_view(),
        name="wishlist",
    ),

    path(
        "cart/",
        views.CartView.as_view(),
        name="cart",
    ),

    path(
        "checkout/",
        views.CheckoutView.as_view(),
        name="checkout",
    ),

    path(
        "razorpay-verify/",
        views.RazorpayVerifyView.as_view(),
        name="razorpay_verify",
    ),

    path(
        "payment/<str:order_id>/",
        views.RazorpayPageView.as_view(),
        name="razorpay_page",
    ),

    path(
        "order-success/",
        views.OrderSuccessView.as_view(),
        name="order_success",
    ),

    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile",
    ),

    path(
        "login/",
        views.LoginView.as_view(),
        name="login",
    ),

    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),

    path(
        "logout/",
        views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "my-orders/",
        views.MyOrdersView.as_view(),
        name="my_orders",
    ),

]