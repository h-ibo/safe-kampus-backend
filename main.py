from fastapi import FastAPI

app = FastAPI(title="SafeKampüs Backend")

@app.get("/")
async def read_root():
    return {"message": "Safe Kampüs Backend Çalışıyor!"}
