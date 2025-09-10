#!/usr/bin/env python3
import os
from pathlib import Path

def load_env():
    env_path = Path(__file__).parent / "env" / "rpi4.env"
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, _, value = line.strip().partition('=')
                os.environ[key] = value

def test_misc():
    import misc
    print("Testing misc.py:")
    try:
        print("Turning on SATA lines...")
        misc.disk_turn_on()
        print("SATA lines turned on.")
    except Exception as e:
        print(f"misc.disk_turn_on test failed: {e}")

    try:
        print("Testing read_key (will block, press button to continue)...")
        import re
        pattern = {'click': re.compile(r'1+0+1{3,}')}  # simple pattern
        result = misc.read_key(pattern, 10)
        print(f"read_key result: {result}")
    except Exception as e:
        print(f"misc.read_key test failed: {e}")

if __name__ == "__main__":
    print("Loading rpi4.env...")
    load_env()
    print("Environment loaded.")
    test_misc()
