import httpx

from core.config import settings


class FaceitClient:
    def __init__(self):
        self.base_url = settings.faceit.base_url
        self.headers = {"Authorization": f"Bearer {settings.faceit.api_key}"}

    async def get_player_details(self, nickname: str):
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
        ) as client:
            response = await client.get("/players", params={"nickname": nickname})

            if response.status_code == 404:  # Player not found
                return None

            response.raise_for_status()
            return response.json()
