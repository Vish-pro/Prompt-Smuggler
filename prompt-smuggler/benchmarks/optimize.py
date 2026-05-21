import os
import json
import yaml
import requests
import argparse
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util

# Load environment variables
load_dotenv()

# Add project root to path so we can import smuggler
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smuggler.compiler import compile_prompt, load_config

def generate_openai(prompt, model="gpt-4o"):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_anthropic(prompt, model="claude-3-5-sonnet-20240620"):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0
    }

    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
    response.raise_for_status()
    return response.json()["content"][0]["text"]

def generate_ollama(prompt, model="llama3", endpoint="http://localhost:11434"):
    url = f"{endpoint}/api/chat"
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.0}
    }

    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["message"]["content"]

def generate_llm_response(prompt, provider, target_model, ollama_endpoint=None):
    try:
        if provider == "openai":
            return generate_openai(prompt, target_model)
        elif provider == "anthropic":
            return generate_anthropic(prompt, target_model)
        elif provider == "ollama":
            return generate_ollama(prompt, target_model, ollama_endpoint)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    except Exception as e:
        print(f"Error generating response from {provider}: {e}")
        return ""

def pass_1_eval(response, expected_structure):
    """
    Pass 1: Hard Structural Assertion.
    """
    if expected_structure == "json":
        # Check if response contains valid JSON
        # Sometimes models wrap in markdown ```json ... ```
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]

        try:
            json.loads(clean_response)
            return True
        except json.JSONDecodeError:
            return False

    return True # If no specific structure, pass

def pass_2_eval(ground_truth, compressed_response, embedding_model):
    """
    Pass 2: Semantic Similarity (Cosine Distance) using SentenceTransformers.
    """
    if not ground_truth or not compressed_response:
        return 0.0

    emb1 = embedding_model.encode(ground_truth, convert_to_tensor=True)
    emb2 = embedding_model.encode(compressed_response, convert_to_tensor=True)

    cosine_scores = util.cos_sim(emb1, emb2)
    return cosine_scores[0][0].item()

def iterate_and_optimize(prompts, provider, target_model, ollama_endpoint, embedding_model, config, config_path):
    print("\nStarting optimization loop...")

    # We will test variations of keys for grammar items
    # Example: instead of µ_j, maybe we use a shorter/different symbol like Ω_j or [J]
    # For MVP, we will run a simple mutation: test [key] vs µ_key to see which one works better.

    original_grammar = config.get("grammar", {}).copy()
    if not original_grammar:
        print("No grammar found to optimize.")
        return

    best_grammar = original_grammar.copy()

    for key, value in original_grammar.items():
        # Generate variations for the shorthand key
        variations = [key] # Original
        if key.startswith("µ_"):
            variations.append(key.replace("µ_", "Ω_")) # Different unicode
            variations.append(f"[{key[2:].upper()}]") # Markdown style like [J]

        best_variant = key
        best_savings = -999999

        print(f"\nOptimizing shorthand for: '{value[:30]}...'")

        for variant in variations:
            print(f"  Testing variant: {variant}")

            # Temporarily apply variant
            test_grammar = best_grammar.copy()
            del test_grammar[key]
            test_grammar[variant] = value

            success = True
            total_savings_for_variant = 0

            # Test this variant across all prompts
            for prompt_data in prompts:
                raw_prompt = prompt_data["raw_prompt"]
                expected_structure = prompt_data.get("expected_structure")

                # Check if this prompt even uses the value
                if value not in raw_prompt:
                    continue

                # Compile with test grammar
                from smuggler.compiler import compile_prompt, generate_grammar_header

                # Substitute value with variant
                test_compressed_text = raw_prompt.replace(value, variant)
                test_grammar_header = generate_grammar_header({variant: value})
                final_compressed_prompt = f"{test_grammar_header}\n\n{test_compressed_text}"

                # We need raw response (ground truth)
                raw_response = generate_llm_response(raw_prompt, provider, target_model, ollama_endpoint)
                if not raw_response:
                    success = False
                    break

                # Get compressed response
                compressed_response = generate_llm_response(final_compressed_prompt, provider, target_model, ollama_endpoint)
                if not compressed_response:
                    success = False
                    break

                # Pass 1
                pass_1 = pass_1_eval(compressed_response, expected_structure)
                if not pass_1:
                    success = False
                    break

                # Pass 2
                similarity = pass_2_eval(raw_response, compressed_response, embedding_model)
                if similarity < 0.85:
                    success = False
                    break

                # Calculate tokens for savings
                from smuggler.tokenizer import calculate_savings
                savings = calculate_savings(raw_prompt, test_compressed_text, test_grammar_header, target_model)
                total_savings_for_variant += savings["saved_tokens"]

            if success:
                print(f"    -> SUCCESS. Tokens saved: {total_savings_for_variant}")
                if total_savings_for_variant > best_savings:
                    best_savings = total_savings_for_variant
                    best_variant = variant
            else:
                print(f"    -> FAILURE (Degraded output or structure mismatch)")

        if best_variant != key:
            print(f"  >> Updating dictionary: {key} -> {best_variant}")
            del best_grammar[key]
            best_grammar[best_variant] = value
            # Update 'key' so subsequent iterations use the new key
            key = best_variant

    # Save optimized config
    if best_grammar != original_grammar:
        print(f"\nOptimization complete. Saving optimized mappings to {config_path}")
        config["grammar"] = best_grammar
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    else:
        print("\nOptimization complete. Existing mappings were already optimal.")


def run_benchmarks(provider="ollama", target_model="llama3", ollama_endpoint="http://localhost:11434", optimize=False):
    print(f"Loading sentence-transformer model (all-MiniLM-L6-v2)...")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    config_path = "../.smugglerrc.yaml"
    config = load_config(config_path)

    with open("test_prompts.json", "r") as f:
        prompts = json.load(f)

    if optimize:
        iterate_and_optimize(prompts, provider, target_model, ollama_endpoint, embedding_model, config, config_path)
        return

    for prompt_data in prompts:
        raw_prompt = prompt_data["raw_prompt"]
        expected_structure = prompt_data.get("expected_structure")

        print(f"\n--- Testing Prompt ID: {prompt_data['id']} ---")

        compressed_text, grammar_header = compile_prompt(raw_prompt, config)
        final_compressed_prompt = f"{grammar_header}\n\n{compressed_text}" if grammar_header else compressed_text

        print(f"1. Fetching ground truth for raw prompt via {provider}...")
        raw_response = generate_llm_response(raw_prompt, provider, target_model, ollama_endpoint)

        print(f"2. Fetching response for compressed prompt via {provider}...")
        compressed_response = generate_llm_response(final_compressed_prompt, provider, target_model, ollama_endpoint)

        print("3. Evaluating...")
        # Pass 1
        pass_1 = pass_1_eval(compressed_response, expected_structure)
        print(f"   Pass 1 (Structure='{expected_structure}'): {'PASS' if pass_1 else 'FAIL'}")

        # Pass 2
        similarity = pass_2_eval(raw_response, compressed_response, embedding_model)
        print(f"   Pass 2 (Semantic Similarity): {similarity:.4f}")

        if pass_1 and similarity > 0.85:
            print("   -> Result: SUCCESS (Compression rule safe)")
        else:
            print("   -> Result: FAILURE (Compression rule degraded output)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", type=str, default="ollama", choices=["openai", "anthropic", "ollama"])
    parser.add_argument("--model", type=str, default="llama3")
    parser.add_argument("--optimize", action="store_true", help="Run the optimization loop to mutate shorthand keys.")
    args = parser.parse_args()

    config = load_config("../.smugglerrc.yaml")
    endpoint = config.get("settings", {}).get("ollama_endpoint", "http://localhost:11434")

    run_benchmarks(args.provider, args.model, endpoint, optimize=args.optimize)
