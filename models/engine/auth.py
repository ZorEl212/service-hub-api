import os

from twilio.rest import Client


class AuthEngine:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.verify_sid = os.getenv("TWILIO_VERIFY_SID")
        self.client = Client(self.account_sid, self.auth_token)

    async def send_verification(self, phone_number) -> bool:
        verification = self.client.verify.v2.services(self.verify_sid).verifications.create(
            to=phone_number,
            channel="sms"  # or "call"
        )
        return True if verification.status == "pending" else False

    async def check_verification(self, phone_number, code) -> bool:
        verification_check = self.client.verify.v2.services(self.verify_sid).verification_checks.create(
            to=phone_number,
            code=code
        )
        return True if  verification_check.status == "approved" else False
