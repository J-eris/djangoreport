# middleware.py

from django.utils.deprecation import MiddlewareMixin

class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Agrega el user_id a la solicitud para que esté disponible en todas las vistas
        request.user_id = request.session.get('user_id', None)
