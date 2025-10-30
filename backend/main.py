from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app=FastAPI()

class CodeInput(BaseModel):
    code: str
    languange: str
    framework: str

@app.route("/health")
def health():
    return {"status" :"healthy"}

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)