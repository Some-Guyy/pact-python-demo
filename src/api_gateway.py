from fastapi import FastAPI, APIRouter, HTTPException
import uvicorn
import requests
import os

PORT = 8082
DATABASE_HOST_NAME = "localhost"
DATABASE_PORT = 8083
WORKER_HOST_NAME = "localhost"
WORKER_PORT = 8084

mock_responses = {}

# Add this decorator to external dependencies to allow it to determine whether its in a test environment based on environment variable and provide a mock response when unit/contract testing.
def check_test_env(function):
    def wrapper(*args):
        if os.getenv("PROVIDER_VERIFICATION") == "1": # 1 if in pact test environment, 0 otherwise.
            response = mock_responses[function.__name__]
            if response == "error":
                raise HTTPException(status_code=400, detail="Mock error")
            else:
                return response
            
        else: # If not in test environment, just run the function as per normal
            return function(*args)
    
    return wrapper

router = APIRouter()
app = FastAPI()

@check_test_env
def get_user(user):
    return requests.get(f"http://{DATABASE_HOST_NAME}:{DATABASE_PORT}/getuser/{user}") 

@check_test_env
def call_cube_api(n):
    return requests.get(f"http://{WORKER_HOST_NAME}:{WORKER_PORT}/cube/{n}")

@check_test_env
def call_square_api(n):
    return requests.get(f"http://{WORKER_HOST_NAME}:{WORKER_PORT}/square/{n}")

@app.get("/")
def read_root():
    return "this is api gateway"

@app.get("/cubesquare/{user}")
def get_cube_square(user):
    number = get_user(user).json() # Service C
    cubed = call_cube_api(number).json() # Service D
    cube_squared = call_square_api(cubed).json() # Service D
    return cube_squared

if __name__ == "__main__":
    uvicorn.run("api_gateway:app", port=PORT, reload=True)
