import re

def convert_korean_date_to_iso(date_str):
    # Remove weekday information if present
    date_str = date_str.split('요일')[0].strip()
    
    # Fix incorrect year format (년 instead of 월)
    if '월' in date_str:
        parts = date_str.split('월')
        if len(parts) > 2:  # If there are multiple '월'
            # Keep only the first month occurrence if they're the same
            if parts[1].strip() == parts[2].strip():
                date_str = parts[0] + '년 ' + parts[1].strip() + '월 ' + parts[1].strip() + '일'
    
    # Try the original pattern first
    pattern = r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'
    match = re.search(pattern, date_str)
    if match:
        year, month, day = match.groups()
        month = month.zfill(2)
        day = day.zfill(2)
        return f"{year}-{month}-{day}"
    
    # If no match and we have year and month but no day
    alt_pattern = r'(\d{4})년\s*(\d{1,2})월'
    match = re.search(alt_pattern, date_str)
    if match:
        year, month = match.groups()
        # If we found duplicate months, use the value as the day
        if date_str.count('월') > 1:
            day = month  # Use the month value as the day since they're the same
        else:
            day = '1'  # Default to first day of month if no day specified
        month = month.zfill(2)
        day = day.zfill(2)
        return f"{year}-{month}-{day}"
    
    return None 