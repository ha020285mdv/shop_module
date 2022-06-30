from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages
from django.core.cache import cache
from ishop.models import Purchase


class CustomNewUserGreetingMiddleware(MiddlewareMixin):
    """Middleware to inform customers without any purchases
     about free delivery for new customers.
     Put after MessageMiddleware in any place"""
    def process_request(self, request):
        if request.user.is_authenticated and not Purchase.objects.filter(customer=request.user).exists():
            messages.info(request, 'Buy now to get FREE delivery!')


class CustomUserSurfingCounter(MiddlewareMixin):
    """There are not any benefits, only to try new things"""
    def process_request(self, request):
        if request.user.is_authenticated:
            counter = cache.get('counter', 0)
            counter += 1
            success = counter == 10
            if success:
                msg = f'You are {counter}-th user!'
                messages.success(request, msg)
            cache.set('counter', 0 if success else counter)
