from fastapi import FastAPI

app = FastAPI(title="Yuz-Tut-Backend")

@app.get("/")
def message():
    return {"Yuz Tut": "Backend"}

@app.get("/health")
async def health():
    return {"status": "ok"}


