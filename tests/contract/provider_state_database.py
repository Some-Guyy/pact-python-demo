from fastapi import APIRouter
from pydantic import BaseModel

from src.database import app, users, router as main_router

pact_router = APIRouter()

class ProviderState(BaseModel):
    state: str  # noqa: E999


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
    users["bob"] = 3

def setup_no_user_bob():
    if "bob" in users:
        del users["bob"]
