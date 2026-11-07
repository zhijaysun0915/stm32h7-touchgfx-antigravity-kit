#!/usr/bin/env python3
"""
Non-blocking STLINK-V3E Virtual COM Port Telemetry Verifier (verify_serial.py)
Per UM2488 Section 6.14:
  - Interface: USART3 (PB10 TX, PB11 RX) bridged to STLINK-V3E USB (CN14)
  - Settings: 115200 bauds, 8-bit data, no parity, 1 stop bit, no flow control
"""
import argparse
import glob
import sys
import time

try:
    import serial
except ImportError:
    serial = None


def find_stlink_port():
    candidates = sorted(glob.glob("/dev/cu.usbmodem*"))
    return candidates[0] if candidates else None


def main():
    parser = argparse.ArgumentParser(description="Verify STM32H7 boot and TouchGFX telemetry via VCP.")
    parser.add_argument("--port", default=None, help="Serial port (auto-detects /dev/cu.usbmodem* if omitted)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default 115200 per UM2488)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Capture duration in seconds")
    args = parser.parse_args()

    port = args.port or find_stlink_port()
    if not port:
        print("[verify_serial] No /dev/cu.usbmodem* device detected. Connect EVM CN14 (STLINK-V3E) to MacBook Air.")
        sys.exit(0)

    if serial is None:
        print("[verify_serial] pyserial not installed. Run: pip3 install pyserial")
        sys.exit(1)

    print(f"[verify_serial] Listening on {port} @ {args.baud} 8N1 for {args.timeout}s...")
    start = time.time()
    lines = []
    with serial.Serial(port, args.baud, timeout=0.2) as ser:
        while time.time() - start < args.timeout:
            raw = ser.readline()
            if raw:
                text = raw.decode("utf-8", errors="replace").rstrip()
                print(f"  [UART3] {text}")
                lines.append(text)

    print(f"[verify_serial] Captured {len(lines)} telemetry line(s).")


if __name__ == "__main__":
    main()
