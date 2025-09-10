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


def cleanup_pwm(chip, fun):
    try:
        with open(f"/sys/class/pwm/pwmchip{chip}/unexport", "w") as f:
            f.write(str(fun))
        print(f"Unexported PWM channel {fun} on chip {chip}.")
    except Exception as e:
        print(f"Failed to unexport PWM: {e}")

def test_fan():
    import fan
    import time
    chip = os.environ.get("PWMCHIP", "0")
    funs = os.environ.get("PWM_FUN", "0").split(",")
    pins = []
    try:
        for fun in funs:
            pin = fan.Pwm(chip, fun)
            pin.period_us(40)
            pin.enable(True)
            print(f"Switching PWM fan ON (chip={chip}, fun={fun}) at 40% power...")
            pin.write(0.4)
            pins.append((pin, fun))
        time.sleep(2)
        for pin, fun in pins:
            print(f"Switching PWM fan OFF (chip={chip}, fun={fun})...")
            pin.write(0.0)
            pin.enable(False)
        print("Waiting for fans to stop...")
        time.sleep(1)
        print("Hardware PWM fan test complete.")
    except Exception as e:
        print(f"fan test failed: {e}")
    finally:
        for _, fun in pins:
            cleanup_pwm(chip, fun)

if __name__ == "__main__":
    print("Loading rpi4.env...")
    load_env()
    print("Environment loaded.")
    test_fan()
