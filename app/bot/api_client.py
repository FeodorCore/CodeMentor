import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class UserDTO:
    """DTO пользователя от API."""

    id: int
    telegram_id: int
    username: Optional[str]
    is_admin: bool


@dataclass
class CategoryDTO:
    """DTO категории."""

    id: int
    name: str


@dataclass
class LessonDTO:
    """DTO урока."""

    id: int
    category_id: int
    sort_order: int
    title: str
    content: str


class ApiClient:
    """Асинхронный клиент для взаимодействия с FastAPI бэкендом."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # === USERS ===

    async def sync_user(self, telegram_id: int, username: Optional[str]) -> UserDTO:
        """Регистрация/синхронизация пользователя."""
        client = await self._get_client()
        response = await client.post(
            "/bot/users/sync", json={"telegram_id": telegram_id, "username": username}
        )
        response.raise_for_status()
        data = response.json()
        return UserDTO(**data)

    async def get_user(self, telegram_id: int) -> Optional[UserDTO]:
        """Получить пользователя по Telegram ID."""
        client = await self._get_client()
        response = await client.get(f"/bot/users/{telegram_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return UserDTO(**response.json())

    async def get_completed_lessons(
        self, telegram_id: int, category_id: int
    ) -> list[int]:
        """Получить список ID пройденных уроков в категории."""
        client = await self._get_client()
        response = await client.get(f"/bot/users/{telegram_id}/progress/{category_id}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        return data.get("completed_lessons", [])

    # === CATEGORIES ===

    async def get_categories(self) -> list[CategoryDTO]:
        """Получить все категории."""
        client = await self._get_client()
        response = await client.get("/bot/categories")
        response.raise_for_status()
        return [CategoryDTO(**item) for item in response.json()]

    # === LESSONS ===

    async def get_lessons(self, category_id: int) -> list[LessonDTO]:
        """Получить уроки в категории."""
        client = await self._get_client()
        response = await client.get(f"/bot/categories/{category_id}/lessons")
        response.raise_for_status()
        return [LessonDTO(**item) for item in response.json()]

    async def get_lesson(self, lesson_id: int) -> Optional[LessonDTO]:
        """Получить один урок по ID."""
        client = await self._get_client()
        response = await client.get(f"/bot/lessons/{lesson_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return LessonDTO(**response.json())

    async def update_progress(self, telegram_id: int, lesson_id: int) -> bool:
        """Сохранить прогресс (отметить урок как пройденный)."""
        client = await self._get_client()
        response = await client.post(
            f"/bot/users/{telegram_id}/progress", json={"lesson_id": lesson_id}
        )
        response.raise_for_status()
        return True

    async def get_completed_lessons(
        self, telegram_id: int, category_id: int
    ) -> list[int]:
        client = await self._get_client()
        response = await client.get(f"/bot/users/{telegram_id}/progress/{category_id}")
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return response.json().get("completed_lessons", [])

    async def get_questions(self, lesson_id: int) -> list[dict]:
        client = await self._get_client()
        response = await client.get(f"/bot/lessons/{lesson_id}/questions")
        response.raise_for_status()
        return response.json()

    async def submit_answer(
        self, telegram_id: int, answer_option_id: int, is_correct: bool
    ) -> dict:
        client = await self._get_client()
        response = await client.post(
            "/bot/users/answers",
            json={
                "telegram_id": telegram_id,
                "answer_option_id": answer_option_id,
                "is_correct": is_correct,
            },
        )
        response.raise_for_status()
        return response.json()
