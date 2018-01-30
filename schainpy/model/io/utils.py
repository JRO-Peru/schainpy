"""
Utilities for IO modules
"""

import os
from datetime import datetime

def folder_in_range(folder, start_date, end_date, pattern):
    """
    Check whether folder is bettwen start_date and end_date

    Args:
        folder (str): Folder to check
        start_date (date): Initial date
        end_date (date): Final date
        pattern (str): Datetime format of the folder
    Returns:
        bool: True for success, False otherwise
    """
    try:
        dt = datetime.strptime(folder, pattern)
    except:
        raise ValueError('Folder {} does not match {} format'.format(folder, pattern))
    return start_date <= dt.date() <= end_date
