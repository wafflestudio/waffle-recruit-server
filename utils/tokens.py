from rest_framework_simplejwt.tokens import AccessToken, BlacklistMixin, RefreshToken


class RefreshToken(RefreshToken):
    pass


class AccessToken(BlacklistMixin, AccessToken):
    pass


def jwt_token_of(user):
    refresh = RefreshToken.for_user(user)
    jwt_token = {"refresh": str(refresh), "access": str(refresh.access_token)}
    return jwt_token
