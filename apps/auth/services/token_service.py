from rest_framework_simplejwt.tokens import RefreshToken


class TokenService:
    @staticmethod
    def issue_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
        }

    @staticmethod
    def refresh_tokens(refresh_token: str):
        refresh = RefreshToken(refresh_token)
        refresh.set_jti()
        refresh.set_exp()
        return {
            "accessToken": str(refresh.access_token),
            "refreshToken": str(refresh),
        }
