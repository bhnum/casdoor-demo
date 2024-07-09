from casdoor import AsyncCasdoorSDK
from yarl import URL


class Casdoor(AsyncCasdoorSDK):
    def get_auth_link(
        self,
        redirect_uri: str,
        response_type: str = "code",
        scope: str = "read",
    ) -> str:
        url = self.front_endpoint + "/login/oauth/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": response_type,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": self.application_name,
        }
        return str(URL(url).with_query(params))

    @property
    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {self.client_id}:{self.client_secret}",
        }

    async def enforce(
        self,
        permission_model_name: str,
        sub: str,
        obj: str,
        act: str,
        v3: str | None = None,
        v4: str | None = None,
        v5: str | None = None,
    ) -> bool:
        path = "/api/enforce"
        params = {
            "permissionId": permission_model_name,
        }
        permission_rule = [sub, obj, act, v3, v4, v5]
        async with self._session as session:
            enforce_result = await session.post(
                path, params=params, headers=self.headers, json=permission_rule
            )
            if (
                not isinstance(enforce_result, dict)
                or enforce_result.get("status") != "ok"
            ):
                raise ValueError(f"Casdoor response error: {enforce_result}")
            return enforce_result.get("data")

    async def batch_enforce(
        self, permission_model_name: str, permission_rules: list[list[str]]
    ) -> list[bool]:
        path = "/api/batch-enforce"
        params = {
            "permissionId": permission_model_name,
        }
        async with self._session as session:
            enforce_result = await session.post(
                path, params=params, headers=self.headers, json=permission_rules
            )
            if (
                not isinstance(enforce_result, dict)
                or enforce_result.get("status") != "ok"
            ):
                raise ValueError(f"Casdoor response error: {enforce_result}")
            return enforce_result.get("data")
