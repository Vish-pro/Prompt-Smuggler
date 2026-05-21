import tiktoken
import os

# Cache huggingface tokenizers to avoid repeated loading
_hf_tokenizers = {}

def get_hf_tokenizer(model_name: str):
    try:
        from transformers import AutoTokenizer
    except ImportError:
        return None

    if model_name not in _hf_tokenizers:
        try:
            # Silence tokenizers warnings
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            _hf_tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        except Exception:
            _hf_tokenizers[model_name] = None
    return _hf_tokenizers[model_name]

def count_tokens(text: str, model: str = "cl100k") -> int:
    """
    Returns the number of tokens in a text string.
    Uses tiktoken for OpenAI/Claude models (cl100k_base encoding).
    Uses Hugging Face tokenizers for local models (e.g., meta-llama/Meta-Llama-3-8B).
    Falls back to cl100k_base if all else fails.
    """
    # 1. Direct encoding names or Claude/generic — use cl100k_base
    if model.lower() in ("cl100k", "cl100k_base", "claude", "default"):
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            return len(text) // 4

    # 2. Check if it's an OpenAI model
    if "gpt" in model.lower() or "o1" in model.lower():
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except KeyError:
            pass

    # 2. Check if we should use HuggingFace
    hf_model_id = None
    if "llama3" in model.lower():
        hf_model_id = "meta-llama/Meta-Llama-3-8B"
    elif "mistral" in model.lower():
        hf_model_id = "mistralai/Mistral-7B-v0.1"
    elif "claude" not in model.lower(): # Anthropic uses their own, let's fallback to cl100k_base or if provided hf
        hf_model_id = model

    if hf_model_id:
        hf_tokenizer = get_hf_tokenizer(hf_model_id)
        if hf_tokenizer:
            return len(hf_tokenizer.encode(text))

    # 3. Fallback to cl100k_base
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Ultimate fallback
        return len(text) // 4

def calculate_savings(raw_text: str, compressed_text: str, grammar_text: str = "", model: str = "cl100k") -> dict:
    """
    Calculates the token counts and savings.
    """
    raw_tokens = count_tokens(raw_text, model)
    compressed_tokens = count_tokens(compressed_text, model)
    grammar_tokens = count_tokens(grammar_text, model) if grammar_text else 0

    total_compressed_tokens = compressed_tokens + grammar_tokens
    saved_tokens = raw_tokens - total_compressed_tokens

    return {
        "raw_tokens": raw_tokens,
        "compressed_tokens": compressed_tokens,
        "grammar_tokens": grammar_tokens,
        "total_tokens_sent": total_compressed_tokens,
        "saved_tokens": saved_tokens,
        "compression_ratio": raw_tokens / total_compressed_tokens if total_compressed_tokens > 0 else 1.0
    }
