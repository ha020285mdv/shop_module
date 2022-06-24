from django.urls import path

from ishop.views import GoodsListView, Login, Register, Logout, Account
from ishop.views import AdminRefundView, AdminGoodsView, AdminGoodEditView, AdminGoodAddView


urlpatterns = [
    path('', GoodsListView.as_view(), name='goods'),
    path('account/', Account.as_view(), name='account'),

    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),

    path('admin-refund/', AdminRefundView.as_view(), name='adminrefund'),
    path('admin-goods/', AdminGoodsView.as_view(), name='admingoods'),
    path('admin-good-edit/<int:pk>', AdminGoodEditView.as_view(), name='admingood_edit'),
    path('admin-good-add/', AdminGoodAddView.as_view(), name='admingood_add'),
]
