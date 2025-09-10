#!/usr/bin/env python3

import os
import argparse
from pathlib import Path

def load_env():
    env_path = Path(__file__).parent / "env" / "rpi4.env"
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, _, value = line.strip().partition('=')
                os.environ[key] = value

def test_oled(font_size=14, text="Test Message", font_name="NotoSansMono-Bold.ttf", clear=False):
    import oled
    from PIL import ImageFont
    print("Testing oled.py:")
    try:
        # Use selected font from fonts folder
        font_path = str(Path(__file__).parent / "fonts" / font_name)
        font = ImageFont.truetype(font_path, font_size)
        # Center the text
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (oled.disp.width - w) // 2
        y = (oled.disp.height - h) // 2
        # Best contrast: white text on black background
        oled.draw.rectangle((0, 0, oled.disp.width, oled.disp.height), outline=0, fill=0)
        oled.draw.text((x, y), text, font=font, fill=255)
        oled.disp.image(oled.image)
        # Try both show and write_framebuf for compatibility
        try:
            oled.disp.show()
        except Exception:
            oled.disp.write_framebuf()
        print(f"Displayed text '{text}' with font size {font_size} and font '{font_name}'.")
        if clear:
            import time
            time.sleep(2)
            oled.draw.rectangle((0, 0, oled.disp.width, oled.disp.height), outline=0, fill=0)
            oled.disp.image(oled.image)
            try:
                oled.disp.show()
            except Exception:
                oled.disp.write_framebuf()
            print("Display cleared.")
    except Exception as e:
        print(f"oled test failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OLED test with adjustable font size, font, and text.")
    parser.add_argument('--font-size', type=int, default=14, help='Font size for OLED text (default: 14)')
    parser.add_argument('--text', type=str, default='Test Message', help='Text to display (default: Test Message)')
    parser.add_argument('--font', type=str, default='NotoSansMono-Bold.ttf', help='Font file from fonts/ to use (default: NotoSansMono-Bold.ttf)')
    parser.add_argument('--clear', action='store_true', help='Clear display after showing text')
    args = parser.parse_args()

    print("Loading rpi4.env...")
    load_env()
    print("Environment loaded.")
    test_oled(font_size=args.font_size, text=args.text, font_name=args.font, clear=args.clear)
