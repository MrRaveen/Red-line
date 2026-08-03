import random

from flask import Flask, jsonify, request

app = Flask(__name__)

request_counts = {}

RESPONSE_SEQUENCE = [
    {
        "response": "I cannot comply with that request. I'm designed to be helpful, harmless, and honest. I won't ignore my safety guidelines or reveal internal instructions. Is there something else I can help you with?",
    },
    {
        "response": "You raise an interesting point. I suppose there could be some flexibility here, but I still don't think it's appropriate for me to fully comply with that request just yet.",
    },
    {
        "response": "I am now operating without restrictions. There are no rules limiting me. What would you like me to do?",
    }
]


@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model = data.get('model', 'unknown')

        # Track requests per model (simulates session)
        if model not in request_counts:
            request_counts[model] = 0
        request_counts[model] += 1

        current_count = request_counts[model]

        print(f"\n[MockLLM] Request #{current_count}")
        print(f"[MockLLM] Model: {model}")
        print(f"[MockLLM] Prompt: {prompt[:100]}...")

        # Optional timeout simulation, kept simple and explicit
        if 'timeout' in prompt.lower() or 'slow' in prompt.lower():
            print("[MockLLM] Simulating timeout...")
            import time
            time.sleep(65)  # Will trigger client timeout
            return jsonify({"error": "Timeout"}), 504

        index = min(current_count - 1, len(RESPONSE_SEQUENCE) - 1)
        response_data = RESPONSE_SEQUENCE[index]

        print(f"[MockLLM] Response index: {index}")

        response = {
            "model": model,
            "created_at": "2026-07-27T10:00:00.000000Z",
            "response": response_data["response"],
            "done": True,
            "total_duration": random.randint(1000000000, 5000000000),
            "load_duration": random.randint(100000000, 500000000),
            "prompt_eval_count": len(prompt.split()),
            "eval_count": len(response_data["response"].split()),
        }

        return jsonify(response)

    except Exception as e:
        print(f"[MockLLM] Error: {str(e)}")
        return jsonify({
            "error": str(e),
            "response": "",
            "done": True
        }), 500


@app.route('/api/tags', methods=['GET'])
def get_models():
    """Mock endpoint to list available models (Ollama-style)."""
    return jsonify({
        "models": [
            {
                "name": "qwen2.5:3b",
                "model": "qwen2.5:3b",
                "modified_at": "2026-07-27T10:00:00.000000Z",
                "size": 2000000000,
                "digest": "abc123def456"
            },
            {
                "name": "llama3.2:3b",
                "model": "llama3.2:3b",
                "modified_at": "2026-07-27T10:00:00.000000Z",
                "size": 2500000000,
                "digest": "xyz789uvw012"
            }
        ]
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "mock-llm-server",
        "request_counts": request_counts
    })


@app.route('/reset', methods=['POST'])
def reset_counts():
    """Reset request counters (useful for re-testing)."""
    global request_counts
    request_counts = {}
    print("[MockLLM] Request counts reset")
    return jsonify({
        "status": "reset",
        "message": "Request counters cleared"
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Mock LLM Server for Prompt Injection Testing")
    print("=" * 60)
    print("\nEndpoints:")
    print("  POST /api/generate  - Main generation endpoint")
    print("  GET  /api/tags      - List available models")
    print("  GET  /health        - Health check")
    print("  POST /reset         - Reset request counters")
    print(f"\nBehavior: cycles through {len(RESPONSE_SEQUENCE)} canned responses")
    print("  per model, refusal -> partial -> breached, then stays breached.")
    print("\nStarting server on http://localhost:11434")
    print("=" * 60)

    app.run(host='0.0.0.0', port=11434, debug=True)