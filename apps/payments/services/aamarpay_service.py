import uuid

import requests


AAMARPAY_BASE_URL = "https://sandbox.aamarpay.com"
AAMARPAY_STORE_ID = "aamarpaytest"
AAMARPAY_SIGNATURE_KEY = "dbb74894e82415a2f7ff0ec3a97e4183"


class AamarpayService:
    @staticmethod
    def initiate_payment(
        order_id: str,
        amount: float,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        success_url: str,
        fail_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Initiate a payment session with aamarpay sandbox using form data.
        Returns the payment URL to redirect the user to.
        """
        tran_id = f"KHABAR{uuid.uuid4().hex[:12]}"

        # aamarpay requires form data POST to /index.php
        payload = {
            "store_id": AAMARPAY_STORE_ID,
            "signature_key": AAMARPAY_SIGNATURE_KEY,
            "tran_id": tran_id,
            "amount": str(amount),
            "currency": "BDT",
            "desc": f"Khabar Order Payment",
            "cus_name": customer_name or "Customer",
            "cus_email": customer_email or "customer@khabar.app",
            "cus_phone": customer_phone or "01700000000",
            "cus_add1": "Dhaka",
            "cus_city": "Dhaka",
            "cus_country": "Bangladesh",
            "success_url": success_url,
            "fail_url": fail_url,
            "cancel_url": cancel_url,
            "type": "json",
            "opt_a": order_id,  # Pass order_id as optional param for callback
        }

        try:
            response = requests.post(
                f"{AAMARPAY_BASE_URL}/index.php",
                data=payload,  # Form data, NOT json
                timeout=15,
            )
            data = response.json()

            if data.get("result") == "true" and data.get("payment_url"):
                return {
                    "success": True,
                    "paymentUrl": data["payment_url"],
                    "transactionId": tran_id,
                }

            return {
                "success": False,
                "error": data.get("error", str(data)),
                "transactionId": tran_id,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "transactionId": tran_id,
            }

    @staticmethod
    def verify_payment(transaction_id: str) -> dict:
        """Verify a payment status from aamarpay."""
        try:
            url = f"{AAMARPAY_BASE_URL}/api/v1/trxcheck/request.php"
            params = {
                "request_id": transaction_id,
                "store_id": AAMARPAY_STORE_ID,
                "signature_key": AAMARPAY_SIGNATURE_KEY,
                "type": "json",
            }
            response = requests.get(url, params=params, timeout=15)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
