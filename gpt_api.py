from fastapi import FastAPI
from pydantic import BaseModel
from ai_core_gpt.design import GPTDesign, policy_from_summary_meta
import uvicorn

app = FastAPI(title="Hallucination-Safe GPT API", version="1.0")

class GenerateRequest(BaseModel):
    text: str
    evidence: dict | None = None

@app.post("/generate", response_model=dict)
def generate(req: GenerateRequest):
    policy = policy_from_summary_meta()
    gpt = GPTDesign(
        threshold=getattr(policy, "threshold", 0.9),
        require_evidence=getattr(policy, "require_evidence", False)
    )
    result = gpt.generate(req.text, evidence=req.evidence)
    return result

@app.get("/")
def root():
    return {"message": "API ready. Use POST /generate with JSON body."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
