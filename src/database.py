from fastapi import FastAPI, APIRouter, HTTPException
import uvicorn

PORT = 8083
router = APIRouter()
app = FastAPI()

users = {}

@app.get("/")
def read_root():
    return "this is database"

@app.get("/getuser/{user}")
def get_user(user):
    response = users.get(user)
    if not response:
        raise HTTPException(status_code=404, detail=f"User {user} not found")
    
    return response

if __name__ == "__main__":
    uvicorn.run("database:app", port=PORT, reload=True)
