"""
This module provides functionality to parse runtime log files and extract log entries.
"""

import os
from datetime import datetime

LOG_LEVELS = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'VERBOSE1', 'VERBOSE2']

class RuntimeLogLine:
    """
    A class to represent a single runtime log line.
    Attributes:
    -----------
    timestamp : datetime
        The timestamp of the log entry.
    level : int
        The severity level of the log entry.
    message : str
        The message content of the log entry.
    Methods:
    --------
    __init__(log_line: str):
        Initializes the RuntimeLogLine object by parsing the log line.
    parse_log_line(log_line: str):
        Parses the log line and extracts the timestamp, level, and message.
    """
    timestamp: datetime
    level: int
    message: str

    def __init__(self, log_line: str):
        self.timestamp, self.level, self.message = self.parse_log_line(log_line)

    def parse_log_line(self, log_line: str):
        try:
            timestamp_str, level_str, module, object, message, unused = log_line.split(';', 5)
            if message.startswith('Error invoking ') or message.startswith('Error executing ') or message.startswith('Error running '):
                message = message.split(':')[0]
            timestamp = datetime.strptime(timestamp_str, '%d-%m-%Y %H:%M:%S.%f')
            level = LOG_LEVELS.index(level_str.upper())
            return timestamp, level, message
        except ValueError:
            return datetime.min, -1, "Invalid log line format"

def read_log_files(logs_folder):
    """
    Reads log files from the specified folder and parses them into a list of RuntimeLogLine objects.
    Args:
        logs_folder (str): The path to the folder containing the log files.
    Returns:
        list[RuntimeLogLine]: A list of RuntimeLogLine objects, each representing a parsed log entry.
    Notes:
        - Only files with a '.log' extension are processed.
        - Assumes that each log entry starts with a date in the format 'XX-XX-XXXX' (e.g., '12-31-2022').
        - Consecutive lines belonging to the same log entry are concatenated into a single RuntimeLogLine object.
    """

    log_contents: list[RuntimeLogLine] = []
    for filename in os.listdir(logs_folder):
        if filename.endswith('.log'):
            with open(os.path.join(logs_folder, filename), 'r') as file:
                log_entry = []
                for line in file:
                    if line.strip() and line[2] == '-' and line[5] == '-':  # Check for date format at the start of a new log entry
                        if log_entry:
                            log_contents.append(RuntimeLogLine(' '.join(log_entry).strip()))
                            log_entry = []
                    log_entry.append(line.strip())
                if log_entry:  # Append the last log entry if exists
                    log_contents.append(RuntimeLogLine(' '.join(log_entry).strip()))
    return log_contents

if __name__ == "__main__":
    """
    Reads log files from the specified folder and parses them into a list of RuntimeLogLine objects.

    Args:
        logs_folder (str): The path to the folder containing the log files.

    Returns:
        list[RuntimeLogLine]: A list of RuntimeLogLine objects, each representing a parsed log entry.

    Notes:
        - Only files with a '.log' extension are processed.
        - Assumes that each log entry starts with a date in the format 'XX-XX-XXXX' (e.g., '12-31-2022').
        - Consecutive lines belonging to the same log entry are concatenated into a single RuntimeLogLine object.
    """
    logs_folder = 'Logs'
    log_contents = read_log_files(logs_folder)
    log_contents.sort(key=lambda x: x.timestamp)
    for content in log_contents:
        if content.level <= LOG_LEVELS.index('WARNING') and content.level >= 0:
            print(f'{content.timestamp.strftime("%d-%m-%Y %H:%M:%S")}; {LOG_LEVELS[content.level].ljust(10)}; {content.message}')