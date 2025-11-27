from django.http import HttpResponseForbidden

def teacher_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authentication and request.user.occupation == 'Teacher':
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden('You are not authorized to access this page.')
    return _wrapped_view