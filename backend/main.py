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

        # Estimate coverage based on test comprehensiveness
        coverage = estimate_coverage(input.code, generated_tests, input.language)
        
        return {
            "tests": generated_tests,
            "coverage": coverage,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def estimate_coverage(code: str, tests: str, language: str) -> int:
    """Estimate test coverage based on code and test complexity"""
    
    # Language-specific comment patterns
    comment_chars = {
        'python': '#',
        'javascript': '//'
    }
    
    comment_char = comment_chars.get(language, '#')
    
    # Count meaningful code lines (excluding comments and empty lines)
    code_lines = len([
        l for l in code.split('\n') 
        if l.strip() and not l.strip().startswith(comment_char)
    ])
    
    # Count test lines
    test_lines = len([l for l in tests.split('\n') if l.strip()])
    
    # Count test functions based on language
    if language == 'python':
        test_count = tests.count('def test_')
    elif language == 'javascript':
        # Count test(), it(), describe() blocks
        test_count = (
            tests.count('test(') + 
            tests.count('it(') + 
            tests.count('test.each(')
        )
    else:
        test_count = 0
    
    # Heuristic: more tests relative to code = better coverage
    ratio = test_lines / max(code_lines, 1)
    test_density = test_count / max(code_lines / 10, 1)
    
    coverage = min(int(65 + (ratio * 20) + (test_density * 10)), 95)
    return coverage

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)