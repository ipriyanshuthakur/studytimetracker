from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddSubForm, UserSettingsForm, MySearchForm
from .models import Record, UserSettings
from datetime import datetime, timedelta, date
from collections import defaultdict
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt


def float_to_hours_minutes(value):
    hours = int(value)
    minutes = int((value - hours) * 60)
    if hours > 0 and minutes > 0:
        return f"{hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return "0m"

@csrf_exempt
def home(request):
    if request.user.is_authenticated:
        user_settings, created = UserSettings.objects.get_or_create(user=request.user)
        records = Record.objects.filter(user=request.user)
        now = datetime.now()
        today = now.date()
        completed_records = Record.objects.filter(user=request.user, queue_no__lt=0, start_at__date=today)
        queued_records = Record.objects.filter(user=request.user, queue_no__gt=0,)
        running_records = Record.objects.filter(user=request.user, queue_no=0)
        total_completed = completed_records.count()
        total_queued = queued_records.count()
        total_running = running_records.count()
        # Initialize start_at to None
        start_at = None
        if running_records.exists():
            start_at = running_records[0].start_at.replace(tzinfo=None)
        
        daily_time = user_settings.daily_target_hours if user_settings else None
        daily_hours = int(daily_time)
        daily_minutes = int((60)*(daily_time-daily_hours))
        
        if daily_minutes > 0:
            daily_target = str(daily_hours) + 'h ' + str(daily_minutes) + 'm'
        else:
            daily_target = str(daily_hours) + 'h '
        
        target_date = user_settings.target_date if user_settings else None
        current_date = date.today()
        
        if target_date:
            days_remaining = (target_date - current_date).days
        else:
            days_remaining = None  # No target date provided
        
        context = {
            'daily_target': daily_target,
            'max_queued': user_settings.max_queued if user_settings else None,
            'target': user_settings.target_goal if user_settings else None,
            'd_day': user_settings.target_date if user_settings else None,
            'days_remaining': days_remaining,
            'running_records': running_records,
            'total_running': total_running,
            'completed_records': completed_records,
            'total_completed': total_completed,
            'queued_records': queued_records,
            'total_queued': total_queued,
            'start_at': start_at,
        }
        return render(request, 'home.html', context)

    # Process login form
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.error(request, "There Was An Error Logging In, Please Try Again...")

    return render(request, 'home.html')

@csrf_exempt
def logout_user(request):
	logout(request)
	messages.info(request, "You Have Been Logged Out...")
	return redirect('home')

@csrf_exempt
def progress(request):
    if request.user.is_authenticated:
        user = request.user
        now = datetime.now()
        today = now.date()
        n_days = int(today.weekday()) + 1

        current_week_start = today - timedelta(days=today.weekday())
        prev_week_start = current_week_start - timedelta(days=7)

        # Get the first day of the current month
        first_day_of_month = today.replace(day=1)
        last_day_of_month = today
        total_days_in_month = (last_day_of_month - first_day_of_month).days + 1
        

        running_records = Record.objects.filter(user=user, queue_no=0)

        # Format the date ranges
        this_week_range = f"{current_week_start.strftime('%d %b')} - {(current_week_start + timedelta(days=(n_days-1))).strftime('%d %b')}"
        prev_week_range = f"{prev_week_start.strftime('%d %b')} - {(prev_week_start+timedelta(days=6)).strftime('%d %b')}"
        date_list = [(first_day_of_month + timedelta(days=i)).strftime('%d') for i in range((today - first_day_of_month).days + 1)]
    

        this_week_hours = []
        prev_week_hours = [0.0] * 7
        this_month_hours =[]

        this_week_records = Record.objects.filter(
            user=user,
            start_at__date__range=[current_week_start, current_week_start + timedelta(days=6)],
            queue_no=-1
        )

        prev_week_records = Record.objects.filter(
            user=user,
            start_at__date__range=[prev_week_start, prev_week_start + timedelta(days=6)],
            queue_no=-1
        )

        this_month_records = Record.objects.filter(
            user=user,
            start_at__date__range=[first_day_of_month, today],
            queue_no=-1
        )
        todaysTotal = Record.objects.filter(
            user=user,
            start_at__date=today,
            queue_no=-1
        )


        # Calculate hours for previous week
        for i in range(7):
            thatday = prev_week_start + timedelta(days=i)
            t_time = 0
            completed_thatday = prev_week_records.filter(start_at__date=thatday)
            for record in completed_thatday:
                t_time += round(record.time_taken.total_seconds() / 3600, 1)
            prev_week_hours[i] = t_time

        # Calculate hours for current week
        for i in range(n_days):
            thatday = current_week_start + timedelta(days=i)
            t_time = 0
            completed_thatday = this_week_records.filter(start_at__date=thatday)
            if running_records.exists():
                c_seconds = (now - running_records[0].start_at.replace(tzinfo=None)).total_seconds()
                c_time = round(c_seconds / 3600, 2)
            else:
                c_time = 0
            for record in completed_thatday:
                t_time += round(record.time_taken.total_seconds() / 3600, 1)
            if i == (n_days - 1):
                t_time = round((t_time + c_time), 2)
            this_week_hours.append(t_time)


        # Calculate hours for current month

        for i in range(total_days_in_month):
            thatday = first_day_of_month + timedelta(days=i)
            t_time = 0
            completed_thatday = this_month_records.filter(start_at__date=thatday)
            if running_records.exists():
                c_seconds = (now - running_records[0].start_at.replace(tzinfo=None)).total_seconds()
                c_time = round(c_seconds / 3600, 2)
            else:
                c_time = 0
            for record in completed_thatday:
                t_time += round(record.time_taken.total_seconds() / 3600, 1)
            if i == (total_days_in_month - 1):
                t_time = round((t_time + c_time), 2)
            this_month_hours.append(t_time)
        subname_totals = defaultdict(float)
        for record in this_week_records:
            subname = record.subname
            hours = round(record.time_taken.total_seconds() / 3600,1)
            subname_totals[subname] += hours
        subname_totals_dict = dict(subname_totals)
        thisWeekSub = list(subname_totals_dict.keys())  # Extract keys (subnames)
        thisWeekHours = list(subname_totals_dict.values())  # Extract values (study hours)
        thisWeekHoursTotal = float_to_hours_minutes(sum(thisWeekHours))
        monthTotal=float_to_hours_minutes(sum(this_month_hours))
        monthavg=float_to_hours_minutes(sum(this_month_hours)/total_days_in_month)
        
        barNums=len(thisWeekSub)
        barbgcolors=['rgba(0, 123, 255, 0.6)']*barNums
        barcolors=['rgba(0, 123, 255, 1)']*barNums
        if running_records.exists():
            runing_subject=running_records[0].subname
            running_time = (now - running_records[0].start_at.replace(tzinfo=None)).total_seconds()
            running_time_hrs=round(running_time / 3600,2)
            thisWeekSub.insert(0,runing_subject)
            thisWeekHours.insert(0,running_time_hrs)
            barbgcolors.insert(0,'rgba(40, 167, 69, 0.5)')
            barcolors.insert(0,'rgba(40, 167, 69, 1)')
      


        context = {
            'this_week_hours': this_week_hours,
            'prev_week_hours': prev_week_hours,
            'this_month_hours': this_month_hours,
            'this_week_range': this_week_range,
            'prev_week_range': prev_week_range,
            'date_list': date_list,
            'thisWeekSub': thisWeekSub,
            'thisWeekHours': thisWeekHours,
            'thisWeekHoursTotal': thisWeekHoursTotal,
            'total_this_week_records': this_week_records.count(),
            'todaysTotal': todaysTotal.count(),
            'monthTotal':monthTotal,
            'monthavg':monthavg,
            'this_month_records':this_month_records.count(),
            'first_day_of_month':first_day_of_month,
            'todaydate':today,
            'current_week_start':current_week_start,
            'barbgcolors':barbgcolors,
            'barcolors':barcolors,
            'running_records':running_records

        }

        return render(request, 'progress.html', context)
    else:
        messages.success(request, "You Must Be Logged In To Do That...")
        return redirect('home')

@csrf_exempt
def setting_page(request):
    if request.user.is_authenticated:
        user_settings, created = UserSettings.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = UserSettingsForm(request.POST, instance=user_settings)
            if form.is_valid():
                form.save()
                messages.success(request, "Settings updated successfully.")
                return redirect('setting_page')
        else:
            form = UserSettingsForm(instance=user_settings)
        
        return render(request, 'setting_page.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to access the settings page.")
        return redirect('home')

@csrf_exempt
def register_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			# Authenticate and login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Registered! Welcome!")
			# Create or retrieve UserSettings instance
			user_settings, created = UserSettings.objects.get_or_create(user=user)
			return redirect('home')
	else:
		form = SignUpForm()
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})


@csrf_exempt
def date_range_view(request, start, end):
    if request.user.is_authenticated:
        user=request.user
        now = datetime.now()
        today=now.date()
        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            duration_dates = [(start_date + timedelta(days=i)).strftime('%d/%m') for i in range((end_date - start_date).days + 1)]


            records = Record.objects.filter(
                user=request.user,
                start_at__date__range=[start_date, end_date], 
                queue_no=-1,
                ).order_by('start_at')
            running_records = Record.objects.filter(user=user, queue_no=0)
            formatted_start_date = start_date.strftime('%d %B %Y')
            formatted_end_date = end_date.strftime('%d %B %Y')
            total_days_duration = len(duration_dates)
            duration_hours =[]
            for i in range(total_days_duration):
                thatday = start_date + timedelta(days=i)
                t_time = 0
                completed_thatday = records.filter(start_at__date=thatday)
                if thatday==today and running_records.exists():
                    c_seconds = (now - running_records[0].start_at.replace(tzinfo=None)).total_seconds()
                    c_time = round(c_seconds / 3600, 2)
                else:
                    c_time = 0
                for record in completed_thatday:
                    t_time += round(record.time_taken.total_seconds() / 3600, 1)
                if i == (total_days_duration - 1):
                    t_time = round((t_time + c_time), 2)
                duration_hours.append(t_time)

            subjects = sorted(set(record.subname for record in records))
            grouped_records = {subject: [] for subject in subjects}
            for record in records:
                grouped_records[record.subname].append(record)
          

            total_time_duration=sum(duration_hours)
            daily_avg_duration=total_time_duration/total_days_duration
            daily_avg_duration=float_to_hours_minutes(daily_avg_duration)
            total_time_duration=float_to_hours_minutes(total_time_duration)
            start_at = None
            if running_records.exists():
                start_at = running_records[0].start_at.replace(tzinfo=None)
            context = {
                'records': records,
                'grouped_records':grouped_records,
                'formatted_start_date': formatted_start_date,
                'formatted_end_date': formatted_end_date,
                'total_days_duration':total_days_duration,
                'total_time_duration':total_time_duration,
                'daily_avg_duration':daily_avg_duration,
                'duration_hours':duration_hours,
                'duration_dates': duration_dates,
                'running_records':running_records,
                'start_at':start_at,

            }
            return render(request, 'date_range_records.html', context)
        except ValueError:
            # Handle invalid date format
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')



@csrf_exempt
def sub_list(request, pk):
    if request.user.is_authenticated:
        try:
            sub_list = Record.objects.get(id=pk)
            queue_no = sub_list.queue_no
            if sub_list.queue_no == 0:
                status = "Running"
            elif sub_list.queue_no>=0:
                status = "Queued"
            else:
                status = "Completed"

            context = {
                'sub_list': sub_list,
                'status': status,
                'queue_no': queue_no,
            }

            return render(request, 'record.html', context)
        except Record.DoesNotExist:
            messages.success(request, "No Such Record")
            return redirect('home')
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')


@csrf_exempt
def mark_complete(request, pk):
	if request.user.is_authenticated:
		current_record = Record.objects.get(id=pk)
		current_record.queue_no=-1
		current_record.done_at=datetime.now()
		start_at = current_record.start_at.replace(tzinfo=None)
		done_at = current_record.done_at.replace(tzinfo=None)
		total_time = (done_at-start_at).total_seconds()
		current_record.time_taken = timedelta(seconds=total_time)
		current_record.save()
		messages.success(request, f"Completed Successfully - {current_record.topic}  in {current_record.subname}")
		return redirect('home')
	else:
		messages.success(request, "You Must Be Logged In To Do That...")
		return redirect('home')
@csrf_exempt
def start_subject(request, pk):
	if request.user.is_authenticated:
		running_records = Record.objects.filter(user=request.user, queue_no=0)
		if not running_records.exists():
			current_record = Record.objects.get(id=pk)
			current_record.queue_no=0
			current_record.start_at=datetime.now()
			current_record.save()
			messages.success(request, f"Hurray! , {current_record.topic}  of {current_record.subname} Started...")
		else:
			messages.error(request, f"Can't Start, Currently you are doing {running_records[0].subname}")
		return redirect('home') 
	else:
		messages.error(request, "You Must Be Logged In To Do That...")
		return redirect('home') 


@csrf_exempt
def delete_record(request, pk):
	if request.user.is_authenticated:
		delete_it = Record.objects.get(id=pk)
		delete_it.delete()
		messages.info (request, f"{delete_it.subname}, Deleted...")
		return redirect('home')
	else:
		messages.success(request, "You Must Be Logged In To Do That...")
		return redirect('home')


@csrf_exempt
def add_record(request):
    if not request.user.is_authenticated:
        messages.error(request, "You Must Be Logged In...")
        return redirect('home')
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)
    form = AddSubForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.user=request.user
        # Capitalize the first letter of each word in subname and topic
        record.subname = form.cleaned_data['subname'].title()
        record.topic = form.cleaned_data['topic'].title()
        running_records = Record.objects.filter(user=request.user, queue_no=0)
        queued_records = Record.objects.filter(user=request.user, queue_no__gt=0)

        if not running_records.exists():
            record.queue_no = 0
            record.start_at = datetime.now()
            record.save()
        else:
            if queued_records.count() < user_settings.max_queued:
                record.queue_no = queued_records.count() + 1
                record.save()
            else:
                messages.error(request, "Maximum subjects added for today. Complete them first.")
                return redirect('home')
        messages.success(request, "Subject Added...")
        return redirect('home')
    return render(request, 'add_record.html', {'form': form})


@csrf_exempt
def update_record(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You Must Be Logged In...")
        return redirect('home')

    current_record = Record.objects.get(pk=pk)

    if request.method == 'POST':
        form = AddSubForm(request.POST, instance=current_record)	
        if form.is_valid():
            record = form.save(commit=False)
            record.user=request.user
            record.subname = form.cleaned_data['subname'].title()
            record.topic = form.cleaned_data['topic'].title()
            record.save()
            messages.success(request, "Subject Has Been Updated!")
            return redirect('home')
    else:
        form = AddSubForm(instance=current_record)

    return render(request, 'update_record.html', {'form': form})

@csrf_exempt
def search_page(request):
    if request.user.is_authenticated:
        user=request.user
        now = datetime.now()
        today = now.date()
        thisYear=now.year
        thisMonth=now.month
        firstDayMonth=today.replace(day=1)
        thisYearMonths=[]
        thisMonthDays=[]
        for month in range(1, thisMonth):          
            date = datetime(thisYear, month, 1)
            month_name = date.strftime('%B')
            thisYearMonths.append(month_name)

        thisMonthDays = [(firstDayMonth + timedelta(days=i)).strftime('%Y-%m-%d') for i in range((today - firstDayMonth).days + 1)]

        form = MySearchForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                date_range_start = form.cleaned_data.get('date_range_start')
                date_range_end = form.cleaned_data.get('date_range_end')
                single_date = form.cleaned_data.get('single_date')
                subject = form.cleaned_data.get('findsubject')
                if subject=='':
                    subject= None
                query_parameters = {
                    'start_date': date_range_start,
                    'end_date': date_range_end,
                    'date': single_date,
                    'subjectname': subject,
                }
                query_string = urlencode(query_parameters)

                if subject:
                    return HttpResponseRedirect(f'/search_result/?{query_string}')

                elif subject is None and date_range_start and date_range_end:
                    if date_range_start<date_range_end:
                        url = reverse('date_range_view', args=[date_range_start, date_range_end])
                        return redirect(url)
                    elif date_range_start == date_range_end:
                        url = reverse('records_progress', args=[date_range_start])
                        return redirect(url)
                    else:
                        messages.error(request, "Initial date should not exceeds end Date")

                elif subject is None and single_date:
                    url = reverse('records_progress', args=[single_date])
                    return redirect(url)
                else:
                    messages.error(request, "Invalid Form")
                    return redirect('search_page') 
                
    

        context = {
            'thisYearMonths':thisYearMonths,
            'thisMonthDays':thisMonthDays,
            'thisYear':thisYear,
            'form': form,

        }
        return render(request, 'search_page.html', context)
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')

@csrf_exempt
def records_progress(request, sDate):
    if request.user.is_authenticated:
        user=request.user
        now = datetime.now()
        today=now.date()
        try:
            recordsDate = datetime.strptime(sDate, '%Y-%m-%d').date()
            records = Record.objects.filter(
                user=request.user,
                start_at__date=recordsDate, 
                queue_no=-1,
                ).order_by('start_at')
            running_records = Record.objects.filter(user=user, queue_no=0)
            subnames = defaultdict(float)
            for subject in records:
                subname = subject.subname
                hours = round(subject.time_taken.total_seconds() / 3600,2)
                subnames[subname] += hours
            subname_totals_dict = dict(subnames)
            subjects_list = list(subname_totals_dict.keys())  # Extract keys (subnames)
            subject_hours = list(subname_totals_dict.values())  # Extract values (study hours)
            barNums=len(subjects_list)
            barbgcolors=['rgba(0, 123, 255, 0.6)']*barNums
            barcolors=['rgba(0, 123, 255, 1)']*barNums
            if today==recordsDate and running_records.exists():
                runing_subject=running_records[0].subname
                running_time = (now - running_records[0].start_at.replace(tzinfo=None)).total_seconds()
                running_time_hrs=round(running_time / 3600,2)
                subjects_list.insert(0,runing_subject)
                subject_hours.insert(0,running_time_hrs)
                barbgcolors.insert(0,'rgba(40, 167, 69, 0.5)')
                barcolors.insert(0,'rgba(40, 167, 69, 1)')
            total_studied = float_to_hours_minutes(sum(subject_hours))
            subjects = sorted(set(record.subname for record in records))
            grouped_records = {subject: [] for subject in subjects}
            for record in records:
                grouped_records[record.subname].append(record)
            
            start_at = None
            if running_records.exists():
                start_at = running_records[0].start_at.replace(tzinfo=None)

            context = {
                'records': records,
                'grouped_records':grouped_records,
                'running_records':running_records,
                'recordsDate':recordsDate,
                'total_studied':total_studied,
                'subjects_list':subjects_list,
                'subject_hours':subject_hours,
                'barbgcolors':barbgcolors,
                'barcolors':barcolors,
                'start_at':start_at,

            }
            return render(request, 'records_progress.html', context)
        except ValueError:
            # Handle invalid date format
            messages.error(request, "Invalid date format")
            return redirect('search_page')
    else:
        messages.success(request, "You Must Be Logged In...")
        return redirect('home')




@csrf_exempt
def search_result(request):
    if request.user.is_authenticated:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        date = request.GET.get('date')
        subjectname = request.GET.get('subjectname')
        if subjectname.lower()=='all':
            records = Record.objects.filter(user=request.user, queue_no=-1)
        else:
            records = Record.objects.filter(user=request.user, subname=subjectname, queue_no=-1)
        if date=='None':
            date=None
        if start_date=='None' or end_date=='None':
            start_date=None
            end_date=None 

        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
            records = records.filter(start_at__date=date)

        elif start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            records = records.filter(start_at__date__range=(start_date, end_date))


        total_records=records.count()
        paginator = Paginator(records, 10)
        total_pages=paginator.num_pages

        page = request.GET.get('page')
        try:
            records_page = paginator.page(page)
        except PageNotAnInteger:
            records_page = paginator.page(1)
        except EmptyPage:
            records_page = paginator.page(paginator.num_pages)
        
        context = {
            'start_date': start_date,
            'end_date': end_date,
            'date': date,
            'subjectname': subjectname,
            'records': records_page,
            'total_records':total_records,
            'total_pages': total_pages,
        }
        return render(request, 'search_result.html', context)
    else:
        messages.success(request, "You must be logged in to access this page.")
        return redirect('home')
