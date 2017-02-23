from django.utils import timezone
# write my midllewares
from . import models
from django_awesome.settings import TOKEN_NAME


class BasicMiddleware(object):
    """
    input a handler to instantiate a middleware function,
    input a request as parm of the middleware function，
    if has process_request attr, then handle request
    if has process_response attr, then handle response

    """

    def __init__(self, func=None):
        self.func = func
        super(BasicMiddleware, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            # in general, process_request function only improve request, it hardly return a response
            response = self.process_request(request)
        if callable(self.func) and not response:
            response = self.func(request)
            # process_response function usually improve response and need return the response after improving it
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response


class AuthMiddleware(BasicMiddleware):
    def process_request(self, request):
        request.__user__ = None
        request.auth_error = None
        # get token
        token_value = request.cookies.get(TOKEN_NAME)
        if token_value:
            tokens = models.Tokens.objects.filter(value=token_value)
            # if token is valid
            if not len(tokens) == 0:
                token = tokens[0]
                # if token is expired
                if token.expire_at >= timezone.now() >= token.created_at:
                    users = models.Users.objects.filter(email=token.user_email)
                    # if token.user_email is valid
                    if not len(users) == 0:
                        user = users[0]
                        # if the owner of token is active
                        if user.is_active:
                            # if the current token of the user who owns the token is equal with that token
                            if user.current_token == token:
                                user.password = '**********'
                                request.__user__ = user
                            else:
                                request.auth_error = '你的账号已在别处登录'
                        else:
                            request.auth_error = '此账号已经冻结'
                    else:
                        request.auth_error = '此账号不存在或账号邮箱已更改'
                else:
                    request.auth_error = '登录已过期，请重新登录'
            else:
                request.auth_error = '登录已过期，请重新登录!'
        else:
            request.auth_error = '你还没登录呢~请登录'
