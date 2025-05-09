from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import json
from typing import Dict, List, Any

class PiAIBuilder:
    def __init__(self):
        # Model configuration
        model_name = "facebook/opt-125m"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Enhanced system prompt with examples
        self.system_prompt = """[INST] <<SYS>>
You are CreativeBuildGPT that converts building requests into block layouts. 

Rules:
- Only respond with valid JSON
- Use these block types: block, slab, triangle, semicircle, cylinder, arch
- Coordinates start at (0,0) in bottom-left corner
- Maximum grid size: 10x10

Examples:
1. For "a small house":
{
    "size_x": 3,
    "size_y": 2,
    "blocks": [
        {"type": "block", "x": 0, "y": 0},
        {"type": "block", "x": 1, "y": 0},
        {"type": "block", "x": 2, "y": 0},
        {"type": "triangle", "x": 1, "y": 1}
    ]
}

2. For "a tower":
{
    "size_x": 1,
    "size_y": 4,
    "blocks": [
        {"type": "block", "x": 0, "y": 0},
        {"type": "block", "x": 0, "y": 1},
        {"type": "block", "x": 0, "y": 2},
        {"type": "triangle", "x": 0, "y": 3}
    ]
}

Now process this request:
<</SYS>>"""
        
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device="cpu"
        )

    def generate_instructions(self, user_request: str) -> Dict[str, Any]:
        full_prompt = f"{self.system_prompt}\n{user_request}[/INST]"
        
        output = self.generator(
            full_prompt,
            max_length=300,  # Reduced for more focused output
            do_sample=True,
            temperature=0.5,  # Lower for more deterministic results
            top_k=10,
            num_return_sequences=1
        )
        
        # Extract JSON from output
        raw_output = output[0]['generated_text']
        json_str = raw_output.split('{', 1)[-1]  # Get content after first {
        json_str = '{' + json_str.split('}')[0] + '}'  # Get content up to first }
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI output", "raw_output": raw_output}

if __name__ == '__main__':
    pi_ai = PiAIBuilder()
    user_request = "I want to build a skyscraper"
    
    try:
        instructions = pi_ai.generate_instructions(user_request)
        print(json.dumps(instructions, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")