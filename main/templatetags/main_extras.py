from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def format_timedelta(td):
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{int(hours)}h {int(minutes)}m"
    else:
        return f"{int(minutes)}m"

@register.filter
def format_date(value):
    try:
        date_obj = datetime.strptime(value, "%Y-%m-%d")
        return date_obj.strftime("%d %B")
    except ValueError:
        return value


@register.filter
def first_date_of_month(month_name):
    try:
        # Create a mapping of month names to their numeric representation
        month_dict = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        # Get the numeric representation of the month
        month = month_dict.get(month_name, None)
        
        if month:
            # Create a datetime object for the 1st day of the specified month
            first_day = datetime(datetime.now().year, month, 1)
            return first_day.strftime("%Y-%m-01")
        else:
            return month_name
    except ValueError:
        return month_name


@register.filter
def last_date_of_month(month_name):
    try:
        # Create a mapping of month names to their numeric representation
        month_dict = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }

        # Get the numeric representation of the month
        month = month_dict.get(month_name, None)

        if month:
            # Calculate the last day of the specified month
            if month == 12:
                next_month = 1
                next_year = datetime.now().year + 1
            else:
                next_month = month + 1
                next_year = datetime.now().year

            last_day = datetime(next_year, next_month, 1) - timedelta(days=1)

            return last_day.strftime("%Y-%m-%d")
        else:
            return month_name
    except ValueError:
        return month_name

@register.filter
def previous_week_start(current_week_start):
    previous_week_start_date = current_week_start - timedelta(days=7)
    return previous_week_start_date.strftime('%Y-%m-%d')

@register.filter
def remove_year(month_withyear):
    date_obj = datetime.strptime(month_withyear, '%B %Y')
    return date_obj.strftime('%B')

@register.filter
def time_sum(rs):
    total_time = timedelta()
    for r in rs:
        if r.time_taken:
            total_time += r.time_taken
    total_time=format_timedelta(total_time)
    return total_time