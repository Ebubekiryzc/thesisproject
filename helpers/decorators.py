from functools import wraps
from django.contrib.auth.decorators import user_passes_test

def check_user(user):
    return not user.is_authenticated

user_logout_required = user_passes_test(check_user, '/', None)

def auth_user_should_not_access(viewfunc):
    return user_logout_required(viewfunc)

# TODO: Deprecated
def prevent_recursion(func):

    @wraps(func)
    def no_recursion(sender, instance=None, **kwargs):

        if not instance:
            return

        if hasattr(instance, '_dirty'):
            return

        func(sender, instance=instance, **kwargs)

        try:
            if instance is not None:
                instance._dirty = True
                instance.save()
        finally:
            if instance is not None:
                del instance._dirty

    return no_recursion