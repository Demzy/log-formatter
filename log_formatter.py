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



SESSION_START_KEYWORDS = ["SESSION STARTED", "SYSTEM STARTED", "STARTUP", "BOOTING"]
SESSION_END_KEYWORDS = ["SESSION ENDED", "SHUTDOWN", "SYSTEM STOPPED"]

def split_sessions(parsed_lines):
    sessions = []           # holds all complete sessions
    current_session = []    # holds current session lines.

    for line in parsed_lines:
        # Line is a dictionary from parsed_lines()
        # get the message text and uppercase it for comparison
        message = line["message"].upper()

        # checks if this line starts a new session
        if any(keyword in message for keyword in SESSION_START_KEYWORDS):
            
            # If we already have lines, save previous session first
            # This handles crashes (sessions with no end marker)
            if current_session: # Only save if not empty
                sessions.append({
                    "lines"     : current_session,
                    "status"  : "INCOMPLETE" # no proper end found
                })


                #Start fresh session
                # [line] creates a new list containing just this line
            current_session = [line]

        # Check if this line ends a session
        elif any(keyword in message for keyword in SESSION_END_KEYWORDS):
            
            # add this final line to current session
            current_session.append(line)

            # save as complete: had proper start and end
            sessions.append({
                "lines"     : current_session,
                "status"  : "COMPLETE" # proper shutdown found
            })
            current_session = [] # reset for next session
        # Normal line - just add to current session
        else:
            current_session.append(line)

    # handles remaining lines after loop ends
    # if current_session has lines but never got a proper end 
    # That means crash or monitor is still running
    if current_session:
        sessions.append({
            "lines"     : current_session,
            "status"  : "INCOMPLETE" # incomplete - possible crash
        })

    return sessions
    # returns list of session dictionaries
    # each session has "lines and "status"


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

# Test split_sessions
print("\nTesting session splitter...")
print("=" * 50)

test_log = [
    "system startd successfully",
    "INFO loading drivers",
    "WARNINg disk slow",
    "ERROR disk failed",
    "system shutdown cleanly",
    "system started sucessfully",
    "INFO all system normal",
]

# parse every line first
parsed = [parse_line(line) for line in test_log]

# split into sessions
sessions = split_sessions(parsed)

print(f"Found {len(sessions)} sessions")
for i, session in enumerate(sessions):
    print(f"\nSession {i+1}: {session['status']}")
    print(f"Lines: {len(session['lines'])}")
    for line in session['lines']:
        print(f"    {line['message']}")
