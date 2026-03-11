import argparse
import re
import subprocess

LTSPICE_BIN = "/Applications/LTspice.app/Contents/MacOS/LTspice"

def parse_log(log_path):
    results = {"gain_max": None, "pm": None, "gbw": None}
    pair_pattern = r'\(([0-9eE+\-.]+)dB\s*,\s*([0-9eE+\-.]+)'

    with open(log_path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-16-le", errors="replace")

    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()

        if lower.startswith("gain_max:"):
            m = re.search(pair_pattern, stripped, re.IGNORECASE)
            if m:
                results["gain_max"] = float(m.group(1))

        elif lower.startswith("pm:"):
            m = re.search(pair_pattern, stripped, re.IGNORECASE)
            if m:
                first, second = float(m.group(1)), float(m.group(2))
                if second == 0.0:
                    results["pm"] = 10 ** (first / 20)

        elif lower.startswith("gbw:"):
            m = re.search(pair_pattern, stripped, re.IGNORECASE)
            if m:
                first, second = float(m.group(1)), float(m.group(2))
                if second == 0.0:
                    results["gbw"] = 10 ** (first / 20)

    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--netlist", required=True)
    args = parser.parse_args()

    subprocess.run([LTSPICE_BIN, "-b", args.netlist], timeout=60)

    log_path = args.netlist.replace(".net", ".log")
    results = parse_log(log_path)
    print("--- Parsed values ---")
    for k, v in results.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()