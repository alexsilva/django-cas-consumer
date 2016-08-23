from urllib import urlencode, urlopen

from django.conf import settings
from django.contrib.auth import get_user_model
from .utils import get_config

User = get_user_model()


__all__ = ['CASBackend']

service = settings.CAS_SERVICE
cas_base = settings.CAS_BASE
cas_login = cas_base + get_config('CAS_LOGIN_URL')
cas_validate = cas_base + get_config('CAS_VALIDATE_URL')
cas_logout = cas_base + get_config('CAS_LOGOUT_URL')
cas_next_default = get_config('CAS_NEXT_DEFAULT')


def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """
    params = get_config('CAS_EXTRA_VALIDATION_PARAMS')
    params.update({
        get_config('CAS_TICKET_LABEL'): ticket,
        get_config('CAS_SERVICE_LABEL'): service
    })
    url = cas_validate + '?' + urlencode(params)
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return page.readline().strip()
        else:
            return None
    finally:
        page.close()


class CASBackend(object):
    """CAS authentication backend"""

    def authenticate(self, ticket, service):
        """Verifies CAS ticket and gets or creates User object"""

        username = _verify_cas1(ticket, service)
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user will have an "unusable" password (thanks to James Bennett)
            user = User.objects.create_user(username)
            user.set_unusable_password()
            user.save()
        callback = get_config('CAS_USERINFO_CALLBACK')
        if callback is not None:
            callback(user)
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
