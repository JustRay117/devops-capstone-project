"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"
HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
######################################################################
# VERY BAD TEST CASES because IT SKIPS EVERY OTHER TEST CASES
# def test_root_url_headers(self):
#     """It should have the specified headers and values"""
#     response = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
#     self.assertEqual(response.status_code, status.HTTP_200_OK)

#     Checks each header individually with separate assertEqual calls
#     headers = response.headers
#     self.assertEqual(headers.get("X-Frame-Options"), "SAMEORIGIN")
#     self.assertEqual(headers.get("X-Content-Type-Options"), "nosniff")
#     self.assertEqual(
#         headers.get("Content-Security-Policy"),
#         "default-src 'self'; object-src 'none'"
#     )
#     self.assertEqual(headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

# Check in loop, even if one header fails, the rest will be checked
def test_security_headers(self):
    """It should return security headers"""
    response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    headers = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-Content-Type-Options': 'nosniff',
        'Content-Security-Policy': 'default-src \'self\'; object-src \'none\'',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    for key, value in headers.items():
        self.assertEqual(response.headers.get(key), value)

class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    # READ TEST CASES
    def test_read_an_account(self):
        """It should return a single account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_account = response.get_json()
        response = self.client.get(
            f"{BASE_URL}/{new_account['id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data["id"], new_account["id"])
        self.assertEqual(data["name"], new_account["name"])
        self.assertEqual(data["email"], new_account["email"])
        self.assertEqual(data["address"], new_account["address"])
        self.assertEqual(data["phone_number"], new_account["phone_number"])
        self.assertEqual(data["date_joined"], new_account["date_joined"])

    def test_account_not_found(self):
        """It should return 404 when account is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # UPDATE TEST CASES

    def test_update_account(self):
        """It should Update an existing Account"""
        # create an Account to update
        test_account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=test_account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the account
        new_account = response.get_json()
        new_account["name"] = "New Name"
        response = self.client.put(
            f"{BASE_URL}/{new_account['id']}",
            json=new_account,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check the updated account
        updated_account = response.get_json()
        self.assertEqual(updated_account["name"], "New Name")

    # DELETE TEST CASES

    def test_delete_account(self):
        """It should delete an account"""
        # create an account to delete
        test_account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=test_account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # delete the account
        new_account = response.get_json()
        response = self.client.delete(
            f"{BASE_URL}/{new_account['id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check the account is deleted
        response = self.client.get(
            f"{BASE_URL}/{new_account['id']}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # LIST TEST CASES

    def test_get_accounts_list(self):
        """It should list all customer accounts"""
        # create multiple accounts
        accounts = self._create_accounts(5)
        # get the list of accounts
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(accounts))
        for i, account in enumerate(accounts):
            self.assertEqual(data[i]["id"], account.id)
            self.assertEqual(data[i]["name"], account.name)
            self.assertEqual(data[i]["email"], account.email)
            self.assertEqual(data[i]["address"], account.address)
            self.assertEqual(data[i]["phone_number"], account.phone_number)
            self.assertEqual(data[i]["date_joined"], str(account.date_joined))

    # Error Handlers - Method Not Allowed
    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        response = self.client.delete(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
