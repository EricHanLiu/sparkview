import datetime


def days_in_month_in_daterange(start, end, month, year):
    """
    Calculates how many days are in a certain month within a daterange.
    Example: Oct 28th to Nov 5th has 4 days in October,  this would return 4 for (2018-10-28, 2018-11-05, 10)
    """
    one_day = datetime.timedelta(1)
    date_counter = 0
    cur_date = start
    while cur_date <= end:
        if cur_date.month == month and cur_date.year == year:
            date_counter += 1
        elif cur_date.month > month and cur_date.year == year or cur_date.year > year:
            break
        cur_date = cur_date + one_day

    return date_counter
