import json

import aiohttp

api_uri = "https://enter.tochka.com/uapi/acquiring/v1.0"


class TochkaClient:
    def __init__(self, api_token: str, customer_code: int, success_redirect_url: str, failure_redirect_url: str):
        self.api_token = api_token
        self.customer_code = customer_code
        self.success_redirect_url = success_redirect_url
        self.failure_redirect_url = failure_redirect_url

    async def create_payment_link(self, amount: str, uuid: str):
        request_data = {
            "customerCode": str(self.customer_code),
            "amount": amount,
            "purpose": "Подписка deffun",  # на месяц или год
            "paymentMode": ["sbp", "card"],
            "redirectUrl": self.success_redirect_url,
            "failRedirectUrl": self.failure_redirect_url,
            "consumerId": uuid
        }

        api_request = {
            "Data": request_data
        }

        # Serialize to JSON
        request_json = json.dumps(api_request)

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{api_uri}/payments", data=request_json, headers=headers) as response:
                if response.status == 200:
                    response_json = await response.json()
                    return response_json.get("Data")
                else:
                    response_text = await response.text()
                    raise Exception(f"Request failed with status {response.status}: {response_text}")
