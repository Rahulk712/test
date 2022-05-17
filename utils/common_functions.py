from mail_reader.settings import ACCESS_TOKEN as auth_token
from django.http import JsonResponse

def token_required(func):
    def inner(request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return func(request, *args, **kwargs)
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header is not None:
            tokens = auth_header.split(' ')
            #Authorization: 'Token 2SVpRwv2HAbMccZt22Mw'
            if len(tokens) == 2 and tokens[0] == 'Token':
                if tokens[1] == auth_token:
                    return func(request, *args, **kwargs)
            else:
                return JsonResponse({'error': 'Token mismatch'}, status=401)
        return JsonResponse({'error': 'Access key missing'}, status=401)
    return inner