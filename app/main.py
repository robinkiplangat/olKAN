from fastapi import FastAPI

app = FastAPI(title="olKAN")

@app.get("/")
def root():
    return {"message": "Welcome to olKAN v2.0"}
