from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.core.exceptions import PermissionDenied


class RestrictEmailAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # Allow signup only if their email is in the allowed list
        # By default this will also prevent them from logging in if they don't have an account
        email = sociallogin.account.extra_data.get('email')
        
        # Check if the allowed list is defined
        allowed_emails = getattr(settings, 'ALLOWED_GOOGLE_EMAILS', [])
        
        # Make the check case-insensitive just in case
        if email and email.lower() in [e.lower() for e in allowed_emails]:
            return True
            
        # Deny the login/signup
        raise PermissionDenied("Email is not in the allowed list.")

    def pre_social_login(self, request, sociallogin):
        # We also override this to catch logins of existing users who might have
        # somehow signed up but are no longer in the allowed list.
        email = sociallogin.account.extra_data.get('email')
        allowed_emails = getattr(settings, 'ALLOWED_GOOGLE_EMAILS', [])
        
        if email and email.lower() not in [e.lower() for e in allowed_emails]:
            raise PermissionDenied("Email is not in the allowed list.")
            
        return super().pre_social_login(request, sociallogin)

from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def promote_allowed_user(request, user, **kwargs):
    """
    Automatically promote users whose emails are in ALLOWED_GOOGLE_EMAILS 
    to staff and superuser status upon signup.
    """
    email = user.email
    allowed_emails = getattr(settings, 'ALLOWED_GOOGLE_EMAILS', [])
    
    if email and email.lower() in [e.lower() for e in allowed_emails]:
        user.is_staff = True
        user.is_superuser = True
        user.save()

