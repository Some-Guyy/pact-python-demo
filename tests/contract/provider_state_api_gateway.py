from fastapi import APIRouter
from pydantic import BaseModel

from src.api_gateway import app, mock_responses, router as main_router

pact_router = APIRouter()

class ProviderState(BaseModel):
    state: str  # noqa: E999

# This will be used to instantiate mock response objects during pact verification
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

@pact_router.post("/_pact/provider_states")
async def provider_states(provider_state: ProviderState):
    mapping = {
        "a user named bob exists": setup_user_bob,
        "a user named bob does not exist": setup_no_user_bob,
    }
    mapping[provider_state.state]()

    return {"result": mapping[provider_state.state]}


# Make sure the app includes both routers. This needs to be done after the
# declaration of the provider_states
app.include_router(main_router)
app.include_router(pact_router)

def setup_user_bob():
    mock_responses["get_user"] = MockResponse(200, 3)
    mock_responses["call_cube_api"] = MockResponse(200, 27)
    mock_responses["call_square_api"] = MockResponse(200, 729)

def setup_no_user_bob():
    mock_responses["get_user"] = "error"
    mock_responses["call_cube_api"] = "error"
    mock_responses["call_square_api"] = "error"
