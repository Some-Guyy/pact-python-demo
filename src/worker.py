from fastapi import FastAPI
import uvicorn

PORT = 8084
app = FastAPI()

@app.get("/")
def read_root():
    return "this is worker"

@app.get("/square/{n}")
def square(n):
    n = int(n)
    return n*n

@app.get("/cube/{n}")
def cube(n):
    n = int(n)
    return n*n*n

if __name__ == "__main__":
    uvicorn.run("worker:app", port=PORT, reload=True)
