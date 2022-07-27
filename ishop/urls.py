from django.urls import path, include
from rest_framework import routers

from ishop.API.resources import GoodsViewSet, ShopUserViewSet, PurchaseViewSet, RefundViewSet
from ishop.views import Login, Register, Logout, Account
from ishop.views import GoodsListView, PurchaseView, PurchaseRefundView
from ishop.views import AdminRefundView, AdminGoodsView, AdminGoodEditView, AdminGoodAddView, AdminRefundProcessView
from rest_framework.authtoken import views


router = routers.SimpleRouter()
router.register(r'goods', GoodsViewSet)
router.register(r'users', ShopUserViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'refunds', RefundViewSet)


urlpatterns = [
    path('', GoodsListView.as_view(), name='goods'),
    path('account/', Account.as_view(), name='account'),
    path('purchase/', PurchaseView.as_view(), name='purchase'),
    path('refund/', PurchaseRefundView.as_view(), name='purchase_refund'),

    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),

    path('admin-refund/', AdminRefundView.as_view(), name='adminrefund'),
    path('admin-refund-process/', AdminRefundProcessView.as_view(), name='adminrefund_process'),
    path('admin-goods/', AdminGoodsView.as_view(), name='admingoods'),
    path('admin-good-edit/<int:pk>', AdminGoodEditView.as_view(), name='admingood_edit'),
    path('admin-good-add/', AdminGoodAddView.as_view(), name='admingood_add'),

    path('api/token-auth/', views.obtain_auth_token),
    path('api/', include(router.urls)),
]
