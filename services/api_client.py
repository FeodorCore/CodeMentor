import aiohttp
from config import API_BASE_URL, API_KEY

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }

    async def register_user(self, tg_id: int, username: str = None, full_name: str = None):
        async with aiohttp.ClientSession() as session:
            payload = {
                "tg_id": tg_id,
                "username": username,
                "full_name": full_name
            }
            async with session.post(f"{self.base_url}/users/register", json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    async def get_articles(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/articles", headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []

    async def get_article(self, article_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/articles/{article_id}", headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    async def get_quiz(self, article_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/articles/{article_id}/quiz", headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None

    async def check_answer(self, tg_id: int, question_id: int, answer_id: int):
        async with aiohttp.ClientSession() as session:
            payload = {
                "tg_id": tg_id,
                "question_id": question_id,
                "answer_id": answer_id
            }
            async with session.post(f"{self.base_url}/quiz/check", json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return {"correct": False, "explanation": "Ошибка проверки"}

api_client = APIClient()