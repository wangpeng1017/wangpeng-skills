#!/usr/bin/env python3
"""
Wisart Image Gen — 直接调用 wisart.kuaileshifu.com gpt-image-2 API，返回 PNG 文件。
用法：python3 gen.py "prompt text" output.png [size]
size 默认 1536x1024（横版），可选 1024x1024 / 1024x1536
"""
import sys, os, json, base64, urllib.request, urllib.error

API_KEY  = "sk-1ad2d6b9cb8654dfdb8b1f7bff3eb207"
BASE_URL = "https://wisart.kuaileshifu.com/v1"
MODEL    = "gpt-image-2"

def generate(prompt: str, output: str, size: str = "1536x1024") -> str:
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": "high",
        "response_format": "b64_json"
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}")

    b64 = data["data"][0].get("b64_json") or data["data"][0].get("url")
    if not b64:
        raise RuntimeError(f"Unexpected response: {data}")

    # b64_json → PNG
    img_bytes = base64.b64decode(b64)
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "wb") as f:
        f.write(img_bytes)

    return output

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gen.py 'prompt' output.png [size]")
        sys.exit(1)
    prompt = sys.argv[1]
    out    = sys.argv[2]
    size   = sys.argv[3] if len(sys.argv) > 3 else "1536x1024"
    result = generate(prompt, out, size)
    print(f"✓ saved: {result}")
