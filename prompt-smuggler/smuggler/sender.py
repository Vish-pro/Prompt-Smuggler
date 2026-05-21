import os

DEFAULT_MODELS = {
    # Western providers
    "anthropic":   "claude-sonnet-4-6",
    "openai":      "gpt-4o",
    "bedrock":     "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "ollama":      "llama3.2",
    "gemini":      "gemini-1.5-flash",
    "groq":        "llama-3.3-70b-versatile",
    "mistral":     "mistral-small-latest",
    "azure":       "gpt-4o",
    "huggingface": "meta-llama/Llama-3.2-3B-Instruct",
    # Chinese providers
    "deepseek":    "deepseek-chat",
    "qwen":        "qwen-plus",
    "kimi":        "moonshot-v1-8k",
    "yi":          "yi-lightning",
}

PROVIDERS = list(DEFAULT_MODELS.keys())


def send(prompt: str, provider: str, model: str = None) -> str:
    provider = provider.lower().strip()
    model = model or DEFAULT_MODELS.get(provider)

    dispatch = {
        # Western
        "anthropic":   _send_anthropic,
        "openai":      _send_openai,
        "bedrock":     _send_bedrock,
        "ollama":      _send_ollama,
        "gemini":      _send_gemini,
        "groq":        _send_groq,
        "mistral":     _send_mistral,
        "azure":       _send_azure,
        "huggingface": _send_huggingface,
        # Chinese
        "deepseek":    _send_deepseek,
        "qwen":        _send_qwen,
        "kimi":        _send_kimi,
        "yi":          _send_yi,
    }

    if provider not in dispatch:
        raise ValueError(
            f"Unknown provider '{provider}'.\n"
            f"Available: {' | '.join(PROVIDERS)}"
        )

    return dispatch[provider](prompt, model)


# ── Anthropic ──────────────────────────────────────────────────────────────────
def _send_anthropic(prompt: str, model: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise ImportError("Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ── OpenAI ─────────────────────────────────────────────────────────────────────
def _send_openai(prompt: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── AWS Bedrock ────────────────────────────────────────────────────────────────
def _send_bedrock(prompt: str, model: str) -> str:
    try:
        import boto3
    except ImportError:
        raise ImportError("Run: pip install boto3")

    client = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    )
    response = client.converse(
        modelId=model,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
    )
    return response["output"]["message"]["content"][0]["text"]


# ── Ollama (local, free, no API key) ──────────────────────────────────────────
def _send_ollama(prompt: str, model: str) -> str:
    try:
        import requests
    except ImportError:
        raise ImportError("Run: pip install requests")

    endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
    url = f"{endpoint}/api/chat"

    response = requests.post(url, json={
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }, timeout=120)

    if response.status_code != 200:
        raise EnvironmentError(
            f"Ollama returned {response.status_code}. "
            f"Is Ollama running? Start it with: ollama serve"
        )

    return response.json()["message"]["content"]


# ── Google Gemini ──────────────────────────────────────────────────────────────
def _send_gemini(prompt: str, model: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise ImportError("Run: pip install google-generativeai")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY not set in .env")

    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel(model)
    response = gemini_model.generate_content(prompt)
    return response.text


# ── Groq ───────────────────────────────────────────────────────────────────────
def _send_groq(prompt: str, model: str) -> str:
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Run: pip install groq")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set in .env")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Mistral ────────────────────────────────────────────────────────────────────
def _send_mistral(prompt: str, model: str) -> str:
    try:
        from mistralai import Mistral
    except ImportError:
        raise ImportError("Run: pip install mistralai")

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("MISTRAL_API_KEY not set in .env")

    client = Mistral(api_key=api_key)
    response = client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Azure OpenAI ───────────────────────────────────────────────────────────────
def _send_azure(prompt: str, model: str) -> str:
    try:
        from openai import AzureOpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    api_key  = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    if not api_key:
        raise EnvironmentError("AZURE_OPENAI_API_KEY not set in .env")
    if not endpoint:
        raise EnvironmentError("AZURE_OPENAI_ENDPOINT not set in .env")

    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── HuggingFace Inference API ──────────────────────────────────────────────────
def _send_huggingface(prompt: str, model: str) -> str:
    try:
        from huggingface_hub import InferenceClient
    except ImportError:
        raise ImportError("Run: pip install huggingface-hub")

    token = os.getenv("HF_TOKEN")
    if not token:
        raise EnvironmentError("HF_TOKEN not set in .env")

    client = InferenceClient(token=token)
    response = client.text_generation(prompt, model=model, max_new_tokens=2048)
    return response


# ── DeepSeek ───────────────────────────────────────────────────────────────────
# OpenAI-compatible API. Get key: platform.deepseek.com
def _send_deepseek(prompt: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError("DEEPSEEK_API_KEY not set in .env")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Qwen / Alibaba DashScope ───────────────────────────────────────────────────
# OpenAI-compatible API. Get key: dashscope.aliyun.com
def _send_qwen(prompt: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise EnvironmentError("DASHSCOPE_API_KEY not set in .env")

    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Kimi / Moonshot AI ─────────────────────────────────────────────────────────
# OpenAI-compatible API. Get key: platform.moonshot.cn
def _send_kimi(prompt: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        raise EnvironmentError("MOONSHOT_API_KEY not set in .env")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


# ── Yi / 01.AI ─────────────────────────────────────────────────────────────────
# OpenAI-compatible API. Get key: platform.01.ai
def _send_yi(prompt: str, model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Run: pip install openai")

    api_key = os.getenv("YI_API_KEY")
    if not api_key:
        raise EnvironmentError("YI_API_KEY not set in .env")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.01.ai/v1",
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
