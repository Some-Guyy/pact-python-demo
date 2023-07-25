import atexit
import pytest

from pact import Consumer, Provider, Like
from src.api_gateway import get_user

CONSUMER = "api_gateway"
PROVIDER = "database"
PROVIDER_HOST_NAME = "localhost"
PROVIDER_PORT = 8083

PACT_MOCK_HOST = PROVIDER_HOST_NAME
PACT_MOCK_PORT = PROVIDER_PORT
PACT_DIR = "tests/contract/pacts" # Path from root where pact files will be stored.
LOG_DIR = "tests/contract/log"

PACT_BROKER_PUBLISH = False
PACT_CONSUMER_VERSION = "0.0.0"
PACT_BROKER_URL = "http://localhost:1234"
PACT_BROKER_USERNAME = "pactbroker"
PACT_BROKER_PASSWORD = "pactbroker"

@pytest.fixture(scope="session")
def pact():
    """Setup a Pact Consumer, which provides the Provider mock service. This
    will generate and optionally publish Pacts to the Pact Broker"""

    pact = Consumer(CONSUMER, version=PACT_CONSUMER_VERSION).has_pact_with(
        Provider(PROVIDER),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        pact_dir=PACT_DIR,
        log_dir=LOG_DIR,
        publish_to_broker=PACT_BROKER_PUBLISH,
        broker_base_url=PACT_BROKER_URL,
        broker_username=PACT_BROKER_USERNAME,
        broker_password=PACT_BROKER_PASSWORD
    )

    pact.start_service()

    # Make sure the Pact mocked provider is stopped when we finish, otherwise
    # PACT_MOCK_PORT may become blocked
    atexit.register(pact.stop_service)

    yield pact

    pact.stop_service()

def test_pact_get_existing_user_number(pact):
    input = "bob"
    expected = 3

    (pact
     .given('a user named bob exists')
     .upon_receiving('a request for get user api with a username bob')
     .with_request('get', f'/getuser/{input}')
     .will_respond_with(200, body=Like(expected)))
    
    with pact:
        result = get_user(input).json()
        assert result == expected

def test_pact_get_missing_user_number(pact):
    input = "bob"
    expected = {'detail': "Not Found"}

    (pact
     .given('a user named bob does not exist')
     .upon_receiving('a request for get user api with a username bob')
     .with_request('get', f'/getuser/{input}')
     .will_respond_with(404, body=Like(expected)))
    
    with pact:
        result = get_user(input).json()
        assert result == expected
