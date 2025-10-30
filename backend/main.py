from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import openai
import os

app=FastAPI()

class CodeInput(BaseModel):
    code: str
    language: str
    framework: str

@app.get("/health")
def health():
    return {"status" :"healthy"}

@app.post("/api/generate-tests")
async def generate_tests(input: CodeInput):
    """Generate unit tests using OpenAI"""
    
    prompt = f"""You are an expert test engineer. Generate comprehensive unit tests for this {input.language} code using {input.framework}.

                Include:
                - Normal test cases
                - Edge cases and boundary conditions
                - Error handling tests
                - Descriptive test names and docstrings
                - Mock tests where appropriate

                Code to test:
                ```{input.language}
                {input.code}
                ```

                Generate ONLY the test code with proper imports. No explanations or markdown."""

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        generated_tests = response.choices[0].message.content
        
        return {
            "tests": generated_tests,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)