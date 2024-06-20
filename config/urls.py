"""Root URL configuration.

The student list is the application, so it answers at `/`.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
)
from django.urls import include, path

from students.forms import StyledAuthenticationForm, StyledPasswordChangeForm

urlpatterns = [
    path('admin/', admin.site.urls),
    # Routes are listed explicitly rather than via include('django.contrib.auth.urls').
    # That include also wires the four password-RESET views, which email a token —
    # and there is no EMAIL_BACKEND here, so the flow would accept an address and
    # silently deliver nothing. A broken feature is worse than an absent one.
    path(
        'accounts/login/',
        LoginView.as_view(authentication_form=StyledAuthenticationForm),
        name='login',
    ),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path(
        'accounts/password_change/',
        PasswordChangeView.as_view(form_class=StyledPasswordChangeForm),
        name='password_change',
    ),
    path(
        'accounts/password_change/done/',
        PasswordChangeDoneView.as_view(),
        name='password_change_done',
    ),
    path('', include('students.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
