"""Pre-class setup checker for RAG Lab Interactive.

Run this before class starts (or have students run it themselves) to
catch the common setup problems before they turn into 20 raised hands at
once: missing dependencies, an unset or invalid API key, and a port
already in use.

Usage:
    python3 check_setup.py            # checks everything except a live API call
    python3 check_setup.py --live     # also makes one real (cheap) call to Claude to confirm the key works
"""

import importlib
import socket
import sys
from pathlib import Path

CHECK = "✓"
CROSS = "✗"
WARN = "!"

REQUIRED_PACKAGES = ["flask", "sentence_transformers", "numpy", "anthropic", "dotenv"]


def ok(msg: str) -> None:
    print(f"  [{CHECK}] {msg}")


def fail(msg: str) -> None:
    print(f"  [{CROSS}] {msg}")


def warn(msg: str) -> None:
    print(f"  [{WARN}] {msg}")


def check_python_version() -> bool:
    print("Python version")
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 10):
        ok(f"Python {major}.{minor} (3.10+ required)")
        return True
    fail(f"Python {major}.{minor} found, but 3.10+ is required. Install a newer Python.")
    return False


def check_venv() -> bool:
    print("Virtual environment")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        ok(f"Running inside a virtual environment ({sys.prefix})")
        return True
    warn(
        "Not running inside a virtual environment. This usually still works, but if "
        "imports fail below, run: python3 -m venv .venv && source .venv/bin/activate "
        "&& pip install -r requirements.txt"
    )
    return True  # warning, not a hard failure


def check_dependencies() -> bool:
    print("Dependencies")
    all_ok = True
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            ok(f"{package} importable")
        except ImportError:
            fail(f"{package} NOT found -- run: pip install -r requirements.txt")
            all_ok = False
    return all_ok


def check_env_file() -> tuple[bool, str | None]:
    print(".env file")
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        fail(".env not found -- run: cp .env.example .env, then add your ANTHROPIC_API_KEY")
        return False, None

    ok(".env exists")
    key = None
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("ANTHROPIC_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")
            break

    if not key or key in ("", "your-api-key-here"):
        warn(
            "ANTHROPIC_API_KEY is missing or still the placeholder value. Retrieval/chunking "
            "will work, but generating answers will fail until you add a real key from "
            "console.anthropic.com."
        )
        return True, None

    if not key.startswith("sk-ant-"):
        warn(f"ANTHROPIC_API_KEY doesn't look like a real Anthropic key (expected it to start with 'sk-ant-').")
        return True, key

    ok("ANTHROPIC_API_KEY is set and looks correctly formatted")
    return True, key


def check_port_available(port: int = 5000) -> bool:
    print(f"Port {port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex(("127.0.0.1", port))
    if result != 0:
        ok(f"Port {port} is free")
        return True
    warn(
        f"Something is already listening on port {port}. On macOS this is sometimes the "
        "AirPlay Receiver (System Settings > General > AirDrop & Handoff) -- turn it off, "
        "or run the app with a different port."
    )
    return True  # warning, not a hard failure -- the app will just fail to bind later


def check_live_api_call(key: str) -> bool:
    print("Live API call (--live)")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        client.messages.create(
            model="claude-sonnet-5",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'ok'."}],
        )
        ok("Claude API responded successfully -- your key works")
        return True
    except anthropic.AuthenticationError:
        fail("Claude rejected the API key (401 invalid x-api-key). Check it against console.anthropic.com.")
        return False
    except Exception as exc:  # noqa: BLE001 -- this is a diagnostic script, any failure should be reported
        fail(f"Live API call failed: {exc}")
        return False


def main() -> int:
    live = "--live" in sys.argv
    print("RAG Lab Interactive -- setup check\n" + "=" * 40)

    results = [
        check_python_version(),
        check_venv(),
        check_dependencies(),
    ]
    env_ok, api_key = check_env_file()
    results.append(env_ok)
    results.append(check_port_available())

    if live:
        if api_key:
            results.append(check_live_api_call(api_key))
        else:
            print("Live API call (--live)")
            warn("Skipped -- no usable API key found above.")

    print("=" * 40)
    if all(results):
        print(f"{CHECK} All checks passed. Run: python3 app.py")
        return 0
    print(f"{CROSS} Some checks failed -- fix the items marked [{CROSS}] above before class.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
