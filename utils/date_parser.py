import datetime
from datetime import datetime

def parse_dates(input_string):
    parts = input_string.split()
    dates = []

    for part in parts:
        date_parts = [int(x) for x in part.split('.')]
        day, month, year = None, None, None

        if len(date_parts) == 1:
            day = date_parts[0]
            month = datetime.now().month
            year = datetime.now().year
        elif len(date_parts) == 2:
            day, month = date_parts
            year = datetime.now().year
        elif len(date_parts) == 3:
            day, month, year = date_parts
            if year < 100:
                year += 2000

        try:
            parsed_date = datetime(year, month, day)
            dates.append(parsed_date)
        except ValueError:
            return (datetime(1999, 1, 1), datetime(2999, 1, 1))

    # Handling the case where no valid dates are found
    if not dates:
        return (datetime(1999, 1, 1), datetime(2999, 1, 1))
    
    # Ensuring two dates are always returned
    if len(dates) == 1:
        dates.append(dates[0])  # Duplicate the date if only one is present
    elif len(dates) == 2:
        dates.sort()  # Ensure correct order

    return tuple(dates)
