#!/usr/bin/env python3
import re

SEVERITY_LEVELS = {
    "FATAL"     : 5,
    "CRITICAL"  : 5,
    "ERROR"     : 4,
    "FAILED"    : 4,
    "WARNING"   : 3,
    "WARN"      : 3,
    "INFO"      : 2,
    "OK"        : 1,
    "SUCCESS"   : 1,
}

TIMESTAMP_PATTERNS = [
    (r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "%Y-%m-%d %H:%M:%S"), 
    (r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}", "%d/%m/%Y %H:%M:%S"),
    (r"\d{2}:\d{2}:\d{2}", "%H:%M:%S"),
]

def parse_line(line):

    # empty boc to store results
    # None means "Not found yet"
    # line.strip() removes invisible whitespace
    result = {
        "timestamp" : None,
        "severity"  : None,
        "message"   : line.strip(),
        "level"     : 0
    }

    # Search for timestamp
    # loop through each pattern we know about
    for pattern, date_format in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            result["timestamp"] = match.group()
            break

    line_upper = line.upper()
    for keyword, level in SEVERITY_LEVELS.items():
        if keyword in line_upper:
            result["severity"] = keyword
            result["level"] = level
            break

    return result

if __name__ == "__main__":

    test_lines = [
        "[08:15:32] 48.0° ✅ OK",
        "2026-04-14 08:17:21 ERROR service failed to start",
        "14/04/2026 08:17:21 fATAL system crash",
        "WARNING: memory running low",
        "nothing special about this line",
    ]

    print("Testing log parser...")
    print("=" * 50)

    for line in test_lines:
        parsed = parse_line(line)
        print(f"LINE    : {line[:50]}")
        print(f"TIME    : {parsed['timestamp']}")
        print(f"SEVERITY : {parsed['severity']} (level {parsed['level']})")
        print("-" * 50)

