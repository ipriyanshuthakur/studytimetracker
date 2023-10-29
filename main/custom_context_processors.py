from datetime import datetime, timedelta, date
from .models import Record, UserSettings
from django.db.models import Sum, Q
import os
def record_context(request):
    context = {}

    wallpaper='StudyTime.png'
    if request.user.is_authenticated:
        # Get the current user
        user = request.user
        user_settings, created = UserSettings.objects.get_or_create(user=user)
        wallpaper_number=user_settings.wallpaper_number
        wallpaper_directory = os.path.join("static", "wallpapers")
        wallpaper_files = os.listdir(wallpaper_directory)
        
        try:
            wallpaper = wallpaper_files[wallpaper_number]
        except (IndexError, TypeError):
            wallpaper = 'StudyTime.png'


        now = datetime.now()
        today = now.date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        n_days = int(today.weekday())+1
      
        completed_records = Record.objects.filter(user=user, start_at__date=today, queue_no=-1)
        running_records = Record.objects.filter(user=user, queue_no=0)

        total_time_today_seconds = sum(record.time_taken.total_seconds() for record in completed_records)  
        time_elapsed_seconds = sum((now - record.start_at.replace(tzinfo=None)).total_seconds() for record in running_records)

        # Calculate total time in seconds
        total_time_seconds = total_time_today_seconds + time_elapsed_seconds

        # Calculate hours and minutes
        total_hours, remainder = divmod(int(total_time_seconds), 3600)
        total_minutes = remainder // 60
        if total_hours > 0:
            total_time = f"{total_hours}h {total_minutes}m"
        else:
            total_time = f"{total_minutes}m"

        this_week_total_time_seconds = Record.objects.filter(
            user=user,
            done_at__date__range=[start_of_week, end_of_week],
            queue_no=-1
        ).aggregate(week_time=Sum('time_taken'))['week_time']



        
        if this_week_total_time_seconds:
            this_week_total_time_seconds=this_week_total_time_seconds.total_seconds()+time_elapsed_seconds
            total_week_hours, week_remainder = divmod(this_week_total_time_seconds, 3600)
            total_week_minutes = week_remainder // 60
            if total_week_hours > 0:
                this_week_total_time_formatted = f"{int(total_week_hours)}h {int(total_week_minutes)}m"
            else:
                this_week_total_time_formatted = f"{int(total_week_minutes)}m"

            avg_time_per_day_seconds = this_week_total_time_seconds / n_days
            avg_hours, avg_remainder = divmod(int(avg_time_per_day_seconds), 3600)
            avg_minutes = avg_remainder // 60
            if avg_hours > 0:
                avg_hours_this_week = f"{int(avg_hours)}h {int(avg_minutes)}m"
            else:
                avg_hours_this_week = f"{int(avg_minutes)}m"
            
        else:
            this_week_total_time_formatted = "0m"
            avg_hours_this_week="0m"
        start_at = None
       
        
        context['done_time'] = total_time_today_seconds
        context['total_time'] = total_time
        context['todaysDate'] = today
        context['week_time_taken'] = this_week_total_time_formatted
        context['week_avg'] = avg_hours_this_week
        context['dateToday'] = now.strftime('%d %B %Y')
        context['monthNow'] = now.strftime("%B %Y")
    context['wallpaper'] = wallpaper


    return context
