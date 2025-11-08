from gpt_design import GPTDesign, policy_from_summary_meta

def build_hallucination_resistant_gpt():
    policy = policy_from_summary_meta()
    return GPTDesign(
        threshold=getattr(policy, "threshold", 0.9),
        require_evidence=getattr(policy, "require_evidence", False)
    )

if __name__ == "__main__":
    gpt = build_hallucination_resistant_gpt()
    prompt = input("User Prompt: ")
    result = gpt.generate(prompt)
    print(result["reply"]["answer"])
