import logging

DEBUG = False

if DEBUG:
    logging.basicConfig(
        filename="debug.log",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        force=True,
    )
else:
    logging.disable(logging.CRITICAL)

BASE_URL = "https://aplikace.skolaonline.cz/solapi/api"
TOKEN_URL = f"{BASE_URL}/connect/token"
CLIENT_ID = "test_client"
