from fastapi import FastAPI
import uvicorn
import requests

API_GATEWAY_HOST_NAME = "localhost"
API_GATEWAY_PORT = 8082
PORT = 8081
app = FastAPI()

def call_cube_square_api(user):
    return requests.get(f"http://{API_GATEWAY_HOST_NAME}:{API_GATEWAY_PORT}/cubesquare/{user}")

@app.get("/")
def read_root():
    return "this is frontend"

@app.get("/getcubesquareof/{user}")
def get_cube_square(user):
    return f"The cube square of {user}'s number is {call_cube_square_api(user).json()}" # Service B

if __name__ == "__main__":
    uvicorn.run("frontend:app", port=PORT, reload=True)
