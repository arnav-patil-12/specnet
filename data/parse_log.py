import re
import csv
import sys

def parse_log(log_path):
    # file is UTF-16-LE encoded (LTspice for Mac)
    with open(log_path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-16-le")

    # lines look like: .step w1=0.0005 w3=0.001 w5=0.002
    step_params = []
    step_re = re.compile(
        # python string magic to extract scientific notation numbers
        r"\.step\s+w1=([\d.eE+\-]+)\s+w3=([\d.eE+\-]+)\s+w5=([\d.eE+\-]+)"
    )
    for m in step_re.finditer(text):
        step_params.append({
            "w1": float(m.group(1)),
            "w3": float(m.group(2)),
            "w5": float(m.group(3)),
        })

    n_steps = len(step_params)

    def parse_db_angle_block(block_text, n):
        # returns a list of dB values, one per step taken
        row_re = re.compile(
            # extracts the maximum (DC) gain value
            r"^\s*(\d+)\t\(([\d.eE+\-]+)dB,[^)]+\)",
            re.MULTILINE,
        )
        results = [None] * n
        for m in row_re.finditer(block_text):
            idx = int(m.group(1)) - 1
            if 0 <= idx < n:
                results[idx] = float(m.group(2))
        return results

    def parse_plain_block(block_text, n):
        # returns a list of floating point values
        row_re = re.compile(
            # more python string magic to extract sci. numbers
            r"^\s*(\d+)\t([\d.eE+\-]+)\s*$",
            re.MULTILINE,
        )
        results = [None] * n
        for m in row_re.finditer(block_text):
            idx = int(m.group(1)) - 1
            if 0 <= idx < n:
                results[idx] = float(m.group(2))
        return results

    def parse_phase_at_ugf_block(block_text, n):
        # returns two lists, one for dB values and one for freq
        row_re = re.compile(
            r"^\s*(\d+)\t\(([\d.eE+\-]+)dB,[^)]+\)\t([\d.eE+\-]+)",
            re.MULTILINE,
        )
        db_vals   = [None] * n
        freq_vals = [None] * n
        for m in row_re.finditer(block_text):
            idx = int(m.group(1)) - 1
            if 0 <= idx < n:
                db_vals[idx]   = float(m.group(2))
                freq_vals[idx] = float(m.group(3))
        return db_vals, freq_vals

    def extract_block(text, measurement_name):
        pattern = re.compile(
            r"Measurement:\s+" + re.escape(measurement_name) + r"\r?\n(.*?)(?=\r?\nMeasurement:|\Z)",
            re.DOTALL,
        )
        m = pattern.search(text)
        return m.group(1) if m else ""

    # some of these measurements extracted are not used in our data collection
    # but are rquired for LTspice so we collect them nevertheless
    gain_max_block     = extract_block(text, "gain_max")
    ugf_block          = extract_block(text, "ugf")
    phase_at_ugf_block = extract_block(text, "phase_at_ugf")
    pm_block           = extract_block(text, "pm")
    gbw_block          = extract_block(text, "gbw")

    gain_max_dB               = parse_db_angle_block(gain_max_block, n_steps)
    ugf_hz                    = parse_plain_block(ugf_block, n_steps)
    phase_at_ugf_dB, phase_at_ugf_freq = parse_phase_at_ugf_block(phase_at_ugf_block, n_steps)
    pm_dB                     = parse_db_angle_block(pm_block, n_steps)
    gbw_dB                    = parse_db_angle_block(gbw_block, n_steps)

    return step_params, gain_max_dB, ugf_hz, phase_at_ugf_dB, phase_at_ugf_freq, pm_dB, gbw_dB


def write_csv(output_path, step_params, gain_max_dB, ugf_hz,
              phase_at_ugf_dB, phase_at_ugf_freq, pm_dB, gbw_dB):
    headers = [
        "w1", "w3", "w5",
        "gain_max_dB",
        "pm",
        "gbw",
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i, params in enumerate(step_params):
            pm  = 10 ** (pm_dB[i]  / 20) if pm_dB[i]  is not None else None
            gbw = 10 ** (gbw_dB[i] / 20) if gbw_dB[i] is not None else None
            writer.writerow([
                params["w1"],
                params["w3"],
                params["w5"],
                gain_max_dB[i],
                pm,
                gbw,
            ])
    print(f"Wrote {len(step_params)} rows to {output_path}")


if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else "circuit.log"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "circuit_results.csv"

    step_params, gain_max_dB, ugf_hz, phase_at_ugf_dB, phase_at_ugf_freq, pm_dB, gbw_dB = \
        parse_log(log_path)

    write_csv(out_path, step_params, gain_max_dB, ugf_hz,
              phase_at_ugf_dB, phase_at_ugf_freq, pm_dB, gbw_dB)