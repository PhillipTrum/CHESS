from sglang.test.doc_patch import launch_server_cmd
from sglang.utils import wait_for_server, print_highlight
import openai
import argparse

# Available models
MODELS = {
    "qwen2.5-7b": "Qwen/Qwen2.5-7b-Instruct",
    "qwen3-30b": "Qwen/Qwen3-30B-A3B-Instruct-2507",
    "qwen3-30b-thinking": "Qwen/Qwen3-30B-A3B-Thinking-2507",
}

def main():
    parser = argparse.ArgumentParser(description="Launch LLM server with specified model")
    parser.add_argument(
        "--model",
        choices=list(MODELS.keys()),
        default="qwen3-30b",
        help="Model to use (default: qwen3-30b)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    args = parser.parse_args()
    
    model_path = MODELS[args.model]
    print_highlight(f"Launching server with model: {model_path}")
    
    # Launch the server
    server_process, port = launch_server_cmd(
        f"python3 -m sglang.launch_server --model-path {model_path} --host {args.host} --log-level warning"
    )
    
    wait_for_server(f"http://localhost:{port}")
    print_highlight(f"Server is running at http://localhost:{port}")
    
    print_highlight("\n ===========Running test query============")
    
    # Test query
    client = openai.Client(base_url=f"http://127.0.0.1:{port}/v1", api_key="None")
    
    response = client.chat.completions.create(
        model=model_path,
        messages=[
            {"role": "user", "content": "List 3 countries and their capitals."},
        ],
        temperature=0,
        max_tokens=64,
    )
    print_highlight(response)

if __name__ == "__main__":
    main()