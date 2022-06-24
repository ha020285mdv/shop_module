from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages

from ishop.forms import CustomUserCreationForm
from ishop.models import Good, ShopUser, Purchase, Refund


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class GoodsListView(ListView):
    paginate_by = 10
    http_method_names = ['post', 'get']
    template_name = 'goods_list.html'
    queryset = Good.objects.filter(in_stock__gt=0)
    extra_context = {'title': 'Online shop'}

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            msg = "Only logged users can buy"
            messages.warning(self.request, msg)
            return redirect('login')

        user = ShopUser.objects.get(id=request.user.id)
        good = Good.objects.get(id=self.request.POST['pk'])
        quantity = int(self.request.POST['quantity'])
        price = int(self.request.POST['price'])
        in_stock = good.in_stock
        wallet = user.wallet
        amount = quantity * price

        if wallet < amount:
            msg = "You don't have enough money for this purchase"
            messages.error(self.request, msg)
            return redirect('goods')

        if in_stock < quantity:
            msg = "We don't have enough goods in stock"
            messages.warning(self.request, msg)
            return redirect('goods')

        user.wallet -= amount
        user.save()
        good.in_stock -= quantity
        good.save()
        Purchase.objects.create(customer=user, good=good, quantity=quantity, price=price)

        msg = "Your purchase is done"
        messages.success(self.request, msg)

        return self.get(request, *args, **kwargs)


class Account(LoginRequiredMixin, ListView):
    model = Purchase
    paginate_by = 10
    template_name = 'account.html'
    extra_context = {'title': 'My account'}
    time_interval_to_refund = 3  # in minutes

    def get_queryset(self):
        queryset = self.model.objects.filter(customer=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        delta = timezone.now() - timezone.timedelta(minutes=self.time_interval_to_refund)
        context['refund_possible'] = self.model.objects.filter(customer=self.request.user, datetime__gt=delta)
        in_refund = Refund.objects.filter(purchase__in=self.get_queryset())
        context['in_refund'] = in_refund.values_list('purchase__pk', flat=True)
        context['balance'] = ShopUser.objects.get(id=self.request.user.id).wallet
        return context

    def post(self, request, *args, **kwargs):
        purchase = Purchase.objects.get(pk=self.request.POST['pk'])
        delta = timezone.now() - timezone.timedelta(minutes=self.time_interval_to_refund)
        if purchase.datetime < delta:
            msg = 'Your refund time has been expired'
            messages.error(self.request, msg)
            return self.get(request, *args, **kwargs)

        _, is_new = Refund.objects.get_or_create(purchase=purchase)
        if is_new:
            msg = 'Your refund request has been sent. Wait for approving.'
            messages.success(self.request, msg)
        else:
            msg = 'The refund for current purchase already exists. Wait for approving.'
            messages.error(self.request, msg)

        return self.get(request, *args, **kwargs)


class AdminRefundView(SuperUserRequiredMixin, ListView):
    model = Refund
    paginate_by = 10
    template_name = 'admin_refunds.html'
    extra_context = {'title': 'Admin: Purchases to refund'}

    def post(self, request, *args, **kwargs):
        pk = self.request.POST['pk']
        approval = self.request.POST['approval']

        if approval == 'decline':
            self.model.objects.get(pk=pk).delete()
        else:
            refund = self.model.objects.get(pk=pk)
            user = refund.purchase.customer
            good = refund.purchase.good
            quantity = refund.purchase.quantity
            price = refund.purchase.price

            user.wallet += price * quantity
            user.save()

            good.in_stock += quantity
            good.save()

            self.model.objects.get(pk=pk).delete()
            refund.purchase.delete()

        return self.get(request, *args, **kwargs)


class AdminGoodsView(SuperUserRequiredMixin, ListView):
    model = Good
    paginate_by = 20
    template_name = 'admin_goods.html'
    extra_context = {'title': 'Admin: Goods'}


class AdminGoodEditView(SuperUserRequiredMixin, UpdateView):
    model = Good
    fields = ['title', 'description', 'price', 'image', 'in_stock']
    template_name = 'admin_good_edit.html'
    extra_context = {'title': 'Admin: edit'}
    success_url = '/admin-goods'


class AdminGoodAddView(SuperUserRequiredMixin, CreateView):
    model = Good
    template_name = 'admin_good_add.html'
    fields = '__all__'
    success_url = '/admin-goods'
    extra_context = {'title': 'Admin: add new good'}


class Login(LoginView):
    success_url = '/'
    template_name = 'login.html'

    def get_success_url(self):
        return self.success_url


class Register(CreateView):
    User = get_user_model()
    model = User
    form_class = CustomUserCreationForm
    success_url = '/'
    template_name = 'register.html'

    def form_valid(self, form):
        to_return = super().form_valid(form)
        login(self.request, self.object)
        msg = 'You have been successfully registered and logged in!'
        messages.success(self.request, msg)
        return to_return


class Logout(LoginRequiredMixin, LogoutView):
    next_page = '/'
    login_url = 'login/'
