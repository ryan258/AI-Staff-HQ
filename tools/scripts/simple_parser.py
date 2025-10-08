import re

def parse_log_file(log_file_path):
    """Parses a log file to extract entries with a specific keyword.

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        list: A list of log entries containing the keyword 'ERROR'.
    """
    error_entries = []
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                if re.search(r'ERROR', line):
                    error_entries.append(line.strip())
    except FileNotFoundError:
        print(f"Error: The file at {log_file_path} was not found.")
        return None
    return error_entries

if __name__ == '__main__':
    # Example usage:
    # Create a dummy log file for testing
    with open('example.log', 'w') as f:
        f.write("INFO: System startup successful.\n")
        f.write("DEBUG: Connecting to database...\n")
        f.write("ERROR: Failed to connect to database.\n")
        f.write("INFO: Retrying connection...\n")
        f.write("ERROR: Connection timed out.\n")

    errors = parse_log_file('example.log')
    if errors:
        print("Found the following error entries:")
        for error in errors:
            print(error)
