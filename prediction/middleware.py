class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.is_admin = request.user.is_superuser
            request.is_user = not request.user.is_superuser
        else:
            request.is_admin = False
            request.is_user = False
        return self.get_response(request)
