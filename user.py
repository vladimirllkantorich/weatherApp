import hashlib
from dataclasses import dataclass, field
from collections import Counter


class AuthError(Exception):
    pass


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


@dataclass
class AppUser:
    nickname: str
    role: str
    home_city: str
    _password_hash: str
    _city_counts: Counter[str] = field(default_factory=Counter)

    @classmethod
    def create(cls, nickname: str, home_city: str, password: str, role: str = "user") -> "AppUser":
        return cls(
            nickname=nickname,
            role=role,
            home_city=home_city,
            _password_hash=hash_password(password),
        )

    def check_password(self, password: str) -> bool:
        return hash_password(password) == self._password_hash

    def add_city(self, city: str) -> None:
        city = str(city).strip()
        if city:
            self._city_counts[city] += 1

    def total_requests(self) -> int:
        return int(sum(self._city_counts.values()))

    def unique_cities(self) -> int:
        return int(len(self._city_counts))

    def top_cities(self, n: int = 5) -> list[tuple[str, int]]:
        return self._city_counts.most_common(max(0, int(n)))

    def city_counts(self) -> dict[str, int]:
        return dict(self._city_counts)

    def clear_cities(self) -> None:
        self._city_counts.clear()


class UserStore:
    def __init__(self) -> None:
        self._users: dict[str, AppUser] = {}

    def ensure_admin(self, nickname: str, home_city: str, password: str) -> AppUser:
        key = str(nickname).strip().lower()
        if key in self._users:
            return self._users[key]
        admin = AppUser.create(nickname=str(nickname).strip(), home_city=str(home_city).strip(), password=password, role="admin")
        self._users[key] = admin
        return admin

    def add_user(self, nickname: str, home_city: str, password: str, role: str = "user") -> AppUser:
        nickname = str(nickname).strip()
        home_city = str(home_city).strip()
        if not nickname or not home_city or not password:
            raise AuthError("Fill all fields")

        key = nickname.lower()
        if key in self._users:
            raise AuthError("Nickname already exists")

        user = AppUser.create(nickname=nickname, home_city=home_city, password=password, role=role)
        self._users[key] = user
        return user

    def get_user(self, nickname: str) -> AppUser | None:
        return self._users.get(str(nickname).strip().lower())

    def list_users(self) -> list[str]:
        return sorted(u.nickname for u in self._users.values())

    def authenticate(self, nickname: str, password: str) -> AppUser:
        user = self.get_user(nickname)
        if user is None:
            raise AuthError("User not found")
        if not user.check_password(password):
            raise AuthError("Invalid password")
        return user

    def delete_user(self, nickname: str, actor: AppUser) -> None:
        if actor.role != "admin":
            raise AuthError("Access denied")
        key = str(nickname).strip().lower()
        if key not in self._users:
            raise AuthError("User not found")
        del self._users[key]

    def all_stats(self, actor: AppUser) -> dict:
        if actor.role != "admin":
            raise AuthError("Access denied")

        by_city = Counter()
        home_cities = Counter()
        per_user = []
        total = 0

        for u in self._users.values():
            total += u.total_requests()
            by_city.update(u._city_counts)
            home_cities[u.home_city] += 1
            per_user.append(
                {
                    "nickname": u.nickname,
                    "home_city": u.home_city,
                    "total_requests": u.total_requests(),
                    "unique_cities": u.unique_cities(),
                    "top_cities": u.top_cities(3),
                }
            )

        per_user.sort(key=lambda x: x["total_requests"], reverse=True)

        return {
            "total_requests_all_users": total,
            "top_cities_all_users": by_city.most_common(10),
            "home_cities_distribution": home_cities.most_common(),
            "per_user": per_user,
        }
