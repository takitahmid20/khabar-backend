from apps.users.models import User


class UserService:
    @staticmethod
    def update_profile(user: User, data: dict) -> User:
        for field in ["display_name", "avatar_url"]:
            if field in data:
                setattr(user, field, data[field])
        user.save(update_fields=["display_name", "avatar_url", "updated_at"])
        return user
