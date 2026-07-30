from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Routine, Activity, Habit, HabitLog, Todo
from .forms import RoutineForm, ActivityForm, HabitForm, TodoForm

# ==============================================================================
# ROUTINE VIEWS
# ==============================================================================

@login_required
def routine_list(request):
    # Fetch all routines for the logged-in user, ordered by start time
    routines = Routine.objects.filter(user=request.user).order_by('start_time')
    return render(request, 'tracker/routine_list.html', {'routines': routines})


@login_required
def routine_create(request):
    if request.method == 'POST':
        form = RoutineForm(request.POST)
        if form.is_valid():
            routine = form.save(commit=False)
            routine.user = request.user
            routine.save()
            messages.success(request, 'Routine created successfully!')
            return redirect('routine_list')
    else:
        form = RoutineForm()
    return render(request, 'tracker/routine_form.html', {'form': form, 'title': 'Create Routine'})


@login_required
def routine_edit(request, pk):
    routine = get_object_or_404(Routine, id=pk, user=request.user)
    if request.method == 'POST':
        form = RoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Routine updated successfully!')
            return redirect('routine_list')
    else:
        form = RoutineForm(instance=routine)
    return render(request, 'tracker/routine_form.html', {'form': form, 'title': 'Edit Routine'})


@login_required
def routine_delete(request, pk):
    routine = get_object_or_404(Routine, id=pk, user=request.user)
    if request.method == 'POST':
        routine.delete()
        messages.success(request, 'Routine deleted successfully!')
        return redirect('routine_list')
    return render(request, 'tracker/routine_confirm_delete.html', {'routine': routine})


@login_required
def routine_toggle(request, pk):
    routine = get_object_or_404(Routine, id=pk, user=request.user)
    routine.is_completed = not routine.is_completed
    routine.save()
    messages.success(request, f"Routine '{routine.title}' status updated!")
    return redirect(request.META.get('HTTP_REFERER', 'routine_list'))


# ==============================================================================
# ACTIVITY VIEWS
# ==============================================================================

@login_required
def activity_list(request):
    # Fetch all activities for the logged-in user, ordered by date (newest first) and start time
    activities = Activity.objects.filter(user=request.user).order_by('-date', 'start_time')
    return render(request, 'tracker/activity_list.html', {'activities': activities})


@login_required
def activity_create(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()
            messages.success(request, 'Activity logged successfully!')
            return redirect('activity_list')
    else:
        form = ActivityForm()
    return render(request, 'tracker/activity_form.html', {'form': form, 'title': 'Log Activity'})


@login_required
def activity_edit(request, pk):
    activity = get_object_or_404(Activity, id=pk, user=request.user)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activity updated successfully!')
            return redirect('activity_list')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'tracker/activity_form.html', {'form': form, 'title': 'Edit Activity'})


@login_required
def activity_delete(request, pk):
    activity = get_object_or_404(Activity, id=pk, user=request.user)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Activity deleted successfully!')
        return redirect('activity_list')
    return render(request, 'tracker/activity_confirm_delete.html', {'activity': activity})


# ==============================================================================
# HABIT VIEWS & STREAK LOGIC
# ==============================================================================

from django.utils import timezone
import datetime

def calculate_streak(habit):
    # Get all completed logs for this habit, ordered by date descending
    logs = HabitLog.objects.filter(habit=habit, is_completed=True).order_by('-date')
    if not logs.exists():
        return 0

    today = timezone.localdate()
    yesterday = today - datetime.timedelta(days=1)
    
    # If the most recent completion was not today and not yesterday, the streak is broken
    most_recent_date = logs[0].date
    if most_recent_date != today and most_recent_date != yesterday:
        return 0

    streak = 0
    expected_date = most_recent_date
    
    for log in logs:
        if log.date == expected_date:
            streak += 1
            expected_date -= datetime.timedelta(days=1)
        elif log.date < expected_date:
            # There is a gap, streak ends here
            break
            
    return streak


@login_required
def habit_list(request):
    habits = Habit.objects.filter(user=request.user).order_by('created_at')
    today = timezone.localdate()
    
    # Fetch IDs of habits completed today to show checked state in template
    completed_today = HabitLog.objects.filter(
        habit__user=request.user,
        date=today,
        is_completed=True
    ).values_list('habit_id', flat=True)
    
    context = {
        'habits': habits,
        'completed_today': completed_today
    }
    return render(request, 'tracker/habit_list.html', context)


@login_required
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Habit added successfully!')
            return redirect('habit_list')
    else:
        form = HabitForm()
    return render(request, 'tracker/habit_form.html', {'form': form, 'title': 'Add Habit'})


@login_required
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, id=pk, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully!')
        return redirect('habit_list')
    return render(request, 'tracker/habit_confirm_delete.html', {'habit': habit})


@login_required
def habit_toggle(request, pk):
    habit = get_object_or_404(Habit, id=pk, user=request.user)
    today = timezone.localdate()
    
    # Get or create the daily log for this habit
    log, created = HabitLog.objects.get_or_create(habit=habit, date=today)
    
    if not created:
        log.is_completed = not log.is_completed
    else:
        log.is_completed = True
    log.save()
    
    # Recalculate and update streak
    habit.streak = calculate_streak(habit)
    habit.save()
    
    messages.success(request, f"Status updated for '{habit.name}'!")
    return redirect(request.META.get('HTTP_REFERER', 'habit_list'))


# ==============================================================================
# TODO VIEWS
# ==============================================================================

@login_required
def todo_list(request):
    # Fetch todos for the logged-in user, showing incomplete ones first
    todos = Todo.objects.filter(user=request.user).order_by('is_completed', 'due_date')
    return render(request, 'tracker/todo_list.html', {'todos': todos})


@login_required
def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'Task added to checklist!')
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'tracker/todo_form.html', {'form': form, 'title': 'Add Task'})


@login_required
def todo_edit(request, pk):
    todo = get_object_or_404(Todo, id=pk, user=request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'tracker/todo_form.html', {'form': form, 'title': 'Edit Task'})


@login_required
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, id=pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('todo_list')
    return render(request, 'tracker/todo_confirm_delete.html', {'todo': todo})


@login_required
def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, id=pk, user=request.user)
    todo.is_completed = not todo.is_completed
    todo.save()
    messages.success(request, f"Task '{todo.title}' status updated!")
    return redirect(request.META.get('HTTP_REFERER', 'todo_list'))


# ==============================================================================
# SEARCH SYSTEM
# ==============================================================================

from django.db.models import Q

@login_required
def search_results(request):
    query = request.GET.get('q', '').strip()
    activities = Activity.objects.filter(user=request.user)
    habits = Habit.objects.filter(user=request.user)
    todos = Todo.objects.filter(user=request.user)
    
    if query:
        activity_filter = Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)
        habit_filter = Q(name__icontains=query) | Q(habit_type__icontains=query)
        todo_filter = Q(title__icontains=query) | Q(priority__icontains=query)
        
        # Try to see if the query matches a date format (YYYY-MM-DD)
        try:
            parsed_date = datetime.datetime.strptime(query, "%Y-%m-%d").date()
            activity_filter |= Q(date=parsed_date)
            todo_filter |= Q(due_date=parsed_date)
        except ValueError:
            pass
            
        activities = activities.filter(activity_filter)
        habits = habits.filter(habit_filter)
        todos = todos.filter(todo_filter)
        
    context = {
        'query': query,
        'activities': activities,
        'habits': habits,
        'todos': todos,
    }
    return render(request, 'tracker/search_results.html', context)


# ==============================================================================
# DASHBOARD
# ==============================================================================

from django.db.models import Avg, Count, Sum

@login_required
def dashboard(request):
    today = timezone.localdate()
    week_start = today - datetime.timedelta(days=7)
    month_start = today - datetime.timedelta(days=30)
    
    # ---- Today's Summary ----
    today_routines = Routine.objects.filter(user=request.user)
    today_routines_completed = today_routines.filter(is_completed=True).count()
    today_routines_total = today_routines.count()
    
    today_activities = Activity.objects.filter(user=request.user, date=today)
    today_activities_count = today_activities.count()
    
    today_habits = Habit.objects.filter(user=request.user)
    today_habits_completed = HabitLog.objects.filter(
        habit__user=request.user, date=today, is_completed=True
    ).count()
    today_habits_total = today_habits.count()
    
    today_todos_pending = Todo.objects.filter(user=request.user, is_completed=False).count()
    today_todos_completed = Todo.objects.filter(user=request.user, is_completed=True).count()
    
    # ---- Weekly Summary ----
    week_activities = Activity.objects.filter(user=request.user, date__gte=week_start, date__lte=today)
    week_activity_count = week_activities.count()
    week_avg_productivity = week_activities.aggregate(avg=Avg('productivity_score'))['avg'] or 0
    
    # Calculate total working hours this week
    week_total_hours = 0
    for act in week_activities:
        start = datetime.datetime.combine(act.date, act.start_time)
        end = datetime.datetime.combine(act.date, act.end_time)
        diff = (end - start).total_seconds() / 3600
        if diff > 0:
            week_total_hours += diff
    
    week_habits_completed = HabitLog.objects.filter(
        habit__user=request.user, date__gte=week_start, is_completed=True
    ).count()
    week_habits_possible = today_habits_total * 7
    week_habit_rate = round((week_habits_completed / week_habits_possible * 100), 1) if week_habits_possible > 0 else 0
    
    # ---- Notifications ----
    notifications = []
    
    # Pending todos
    pending_todos = Todo.objects.filter(user=request.user, is_completed=False)
    overdue_todos = pending_todos.filter(due_date__lt=today)
    if overdue_todos.exists():
        notifications.append({
            'type': 'danger',
            'message': f'You have {overdue_todos.count()} overdue task{"s" if overdue_todos.count() > 1 else ""}!'
        })
    
    if pending_todos.exists():
        notifications.append({
            'type': 'warning',
            'message': f'You have {pending_todos.count()} pending task{"s" if pending_todos.count() > 1 else ""} in your checklist.'
        })
    
    # Missed habits today
    missed_habits_count = today_habits_total - today_habits_completed
    if missed_habits_count > 0:
        notifications.append({
            'type': 'info',
            'message': f'{missed_habits_count} habit{"s" if missed_habits_count > 1 else ""} not yet completed today.'
        })
    
    # Incomplete routines
    incomplete_routines = today_routines_total - today_routines_completed
    if incomplete_routines > 0:
        notifications.append({
            'type': 'secondary',
            'message': f'{incomplete_routines} routine{"s" if incomplete_routines > 1 else ""} still pending.'
        })
    
    # ---- Recent Activities ----
    recent_activities = Activity.objects.filter(user=request.user).order_by('-date', '-start_time')[:5]
    
    context = {
        # Today
        'today_routines_completed': today_routines_completed,
        'today_routines_total': today_routines_total,
        'today_activities_count': today_activities_count,
        'today_habits_completed': today_habits_completed,
        'today_habits_total': today_habits_total,
        'today_todos_pending': today_todos_pending,
        'today_todos_completed': today_todos_completed,
        # Weekly
        'week_activity_count': week_activity_count,
        'week_avg_productivity': round(week_avg_productivity, 1),
        'week_total_hours': round(week_total_hours, 1),
        'week_habit_rate': week_habit_rate,
        # Notifications
        'notifications': notifications,
        # Recent
        'recent_activities': recent_activities,
    }
    return render(request, 'tracker/dashboard.html', context)


# ==============================================================================
# REPORTS & CHARTS
# ==============================================================================

import json

@login_required
def weekly_report(request):
    today = timezone.localdate()
    week_start = today - datetime.timedelta(days=6)
    
    # Generate list of last 7 days
    days = []
    for i in range(7):
        d = week_start + datetime.timedelta(days=i)
        days.append(d)
    
    # Daily productivity scores for chart
    daily_labels = []
    daily_scores = []
    daily_hours = []
    daily_activity_counts = []
    
    for d in days:
        daily_labels.append(d.strftime('%a %d'))
        day_activities = Activity.objects.filter(user=request.user, date=d)
        
        avg_score = day_activities.aggregate(avg=Avg('productivity_score'))['avg'] or 0
        daily_scores.append(round(avg_score, 1))
        daily_activity_counts.append(day_activities.count())
        
        # Calculate hours for this day
        hours = 0
        for act in day_activities:
            start = datetime.datetime.combine(d, act.start_time)
            end = datetime.datetime.combine(d, act.end_time)
            diff = (end - start).total_seconds() / 3600
            if diff > 0:
                hours += diff
        daily_hours.append(round(hours, 1))
    
    # Task summary
    week_activities = Activity.objects.filter(user=request.user, date__gte=week_start, date__lte=today)
    completed_activities = week_activities.filter(status='COMPLETED').count()
    pending_activities = week_activities.filter(status='PENDING').count()
    
    completed_todos = Todo.objects.filter(user=request.user, is_completed=True).count()
    pending_todos = Todo.objects.filter(user=request.user, is_completed=False).count()
    
    avg_productivity = week_activities.aggregate(avg=Avg('productivity_score'))['avg'] or 0
    
    total_hours = sum(daily_hours)
    
    # Habit stats
    habits = Habit.objects.filter(user=request.user)
    total_habits = habits.count()
    week_habit_logs = HabitLog.objects.filter(
        habit__user=request.user, date__gte=week_start, is_completed=True
    ).count()
    possible_habits = total_habits * 7
    habit_rate = round((week_habit_logs / possible_habits * 100), 1) if possible_habits > 0 else 0
    
    # Category breakdown for pie chart
    categories = {}
    for act in week_activities:
        cat = act.get_category_display()
        start = datetime.datetime.combine(act.date, act.start_time)
        end = datetime.datetime.combine(act.date, act.end_time)
        diff = (end - start).total_seconds() / 3600
        if diff > 0:
            categories[cat] = categories.get(cat, 0) + diff
    
    cat_labels = list(categories.keys())
    cat_values = [round(v, 1) for v in categories.values()]
    
    context = {
        'week_start': week_start,
        'today': today,
        'completed_activities': completed_activities,
        'pending_activities': pending_activities,
        'completed_todos': completed_todos,
        'pending_todos': pending_todos,
        'avg_productivity': round(avg_productivity, 1),
        'total_hours': round(total_hours, 1),
        'habit_rate': habit_rate,
        'week_habit_logs': week_habit_logs,
        'possible_habits': possible_habits,
        # Chart data (serialized to JSON for JavaScript)
        'daily_labels': json.dumps(daily_labels),
        'daily_scores': json.dumps(daily_scores),
        'daily_hours': json.dumps(daily_hours),
        'daily_activity_counts': json.dumps(daily_activity_counts),
        'cat_labels': json.dumps(cat_labels),
        'cat_values': json.dumps(cat_values),
    }
    return render(request, 'tracker/weekly_report.html', context)


@login_required
def monthly_report(request):
    today = timezone.localdate()
    month_start = today - datetime.timedelta(days=29)
    
    # Generate last 30 days grouped by week
    weeks = []
    for i in range(4):
        w_start = month_start + datetime.timedelta(days=i*7)
        w_end = w_start + datetime.timedelta(days=6)
        if w_end > today:
            w_end = today
        weeks.append((w_start, w_end))
    
    # Weekly productivity trend for line chart
    week_labels = []
    week_scores = []
    week_hours_list = []
    
    for w_start, w_end in weeks:
        week_labels.append(f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}")
        w_activities = Activity.objects.filter(user=request.user, date__gte=w_start, date__lte=w_end)
        avg = w_activities.aggregate(a=Avg('productivity_score'))['a'] or 0
        week_scores.append(round(avg, 1))
        
        hours = 0
        for act in w_activities:
            start = datetime.datetime.combine(act.date, act.start_time)
            end = datetime.datetime.combine(act.date, act.end_time)
            diff = (end - start).total_seconds() / 3600
            if diff > 0:
                hours += diff
        week_hours_list.append(round(hours, 1))
    
    # Monthly totals
    month_activities = Activity.objects.filter(user=request.user, date__gte=month_start, date__lte=today)
    month_activity_count = month_activities.count()
    month_avg_productivity = month_activities.aggregate(avg=Avg('productivity_score'))['avg'] or 0
    
    month_total_hours = 0
    for act in month_activities:
        start = datetime.datetime.combine(act.date, act.start_time)
        end = datetime.datetime.combine(act.date, act.end_time)
        diff = (end - start).total_seconds() / 3600
        if diff > 0:
            month_total_hours += diff
    
    # Category breakdown
    categories = {}
    for act in month_activities:
        cat = act.get_category_display()
        start = datetime.datetime.combine(act.date, act.start_time)
        end = datetime.datetime.combine(act.date, act.end_time)
        diff = (end - start).total_seconds() / 3600
        if diff > 0:
            categories[cat] = categories.get(cat, 0) + diff
    
    cat_labels = list(categories.keys())
    cat_values = [round(v, 1) for v in categories.values()]
    
    # Habit analysis for bar chart
    habits = Habit.objects.filter(user=request.user)
    habit_names = []
    habit_completions = []
    for habit in habits:
        habit_names.append(habit.name)
        count = HabitLog.objects.filter(
            habit=habit, date__gte=month_start, is_completed=True
        ).count()
        habit_completions.append(count)
    
    total_habits = habits.count()
    month_habit_logs = HabitLog.objects.filter(
        habit__user=request.user, date__gte=month_start, is_completed=True
    ).count()
    possible_habits = total_habits * 30
    month_habit_rate = round((month_habit_logs / possible_habits * 100), 1) if possible_habits > 0 else 0
    
    context = {
        'month_start': month_start,
        'today': today,
        'month_activity_count': month_activity_count,
        'month_avg_productivity': round(month_avg_productivity, 1),
        'month_total_hours': round(month_total_hours, 1),
        'month_habit_rate': month_habit_rate,
        # Chart data
        'week_labels': json.dumps(week_labels),
        'week_scores': json.dumps(week_scores),
        'week_hours_list': json.dumps(week_hours_list),
        'cat_labels': json.dumps(cat_labels),
        'cat_values': json.dumps(cat_values),
        'habit_names': json.dumps(habit_names),
        'habit_completions': json.dumps(habit_completions),
    }
    return render(request, 'tracker/monthly_report.html', context)


# ==============================================================================
# HABIT ANALYSIS
# ==============================================================================

@login_required
def habit_analysis(request):
    today = timezone.localdate()
    month_start = today - datetime.timedelta(days=29)
    
    habits = Habit.objects.filter(user=request.user)
    
    # Build detailed stats for each habit
    habit_data = []
    for habit in habits:
        total_logs = HabitLog.objects.filter(habit=habit, is_completed=True).count()
        month_logs = HabitLog.objects.filter(
            habit=habit, date__gte=month_start, is_completed=True
        ).count()
        month_rate = round((month_logs / 30) * 100, 1) if total_logs >= 0 else 0
        
        # Find last completed date
        last_log = HabitLog.objects.filter(
            habit=habit, is_completed=True
        ).order_by('-date').first()
        last_done = last_log.date if last_log else None
        
        # Days since last completion
        days_since = (today - last_done).days if last_done else None
        
        habit_data.append({
            'habit': habit,
            'total_logs': total_logs,
            'month_logs': month_logs,
            'month_rate': month_rate,
            'last_done': last_done,
            'days_since': days_since,
        })
    
    # Sort by streak (highest first) for leaderboard
    leaderboard = sorted(habit_data, key=lambda x: x['habit'].streak, reverse=True)
    
    # Good vs Bad count
    good_count = habits.filter(habit_type='GOOD').count()
    bad_count = habits.filter(habit_type='BAD').count()
    
    # Chart data: habit names and their streaks
    chart_names = [h['habit'].name for h in habit_data]
    chart_streaks = [h['habit'].streak for h in habit_data]
    chart_rates = [h['month_rate'] for h in habit_data]
    
    context = {
        'habit_data': habit_data,
        'leaderboard': leaderboard,
        'good_count': good_count,
        'bad_count': bad_count,
        'total_habits': habits.count(),
        'chart_names': json.dumps(chart_names),
        'chart_streaks': json.dumps(chart_streaks),
        'chart_rates': json.dumps(chart_rates),
    }
    return render(request, 'tracker/habit_analysis.html', context)


# ==============================================================================
# IMPROVEMENT SUGGESTIONS (BASIC AI INSIGHTS)
# ==============================================================================

@login_required
def improvement_suggestions(request):
    today = timezone.localdate()
    week_start = today - datetime.timedelta(days=6)
    month_start = today - datetime.timedelta(days=29)
    
    suggestions = []
    
    # ---- 1. Productivity Analysis ----
    week_activities = Activity.objects.filter(
        user=request.user, date__gte=week_start, date__lte=today
    )
    avg_prod = week_activities.aggregate(avg=Avg('productivity_score'))['avg']
    
    if avg_prod is not None:
        avg_prod = round(avg_prod, 1)
        if avg_prod >= 8:
            suggestions.append({
                'icon': '🌟',
                'type': 'success',
                'title': 'Excellent Productivity!',
                'message': f'Your average productivity this week is {avg_prod}/10. Keep up the great work!'
            })
        elif avg_prod >= 5:
            suggestions.append({
                'icon': '📈',
                'type': 'warning',
                'title': 'Room for Improvement',
                'message': f'Your average productivity is {avg_prod}/10. Try to minimize distractions and set smaller, focused goals.'
            })
        else:
            suggestions.append({
                'icon': '⚠️',
                'type': 'danger',
                'title': 'Low Productivity Alert',
                'message': f'Your average productivity is only {avg_prod}/10. Consider breaking tasks into smaller chunks and taking regular breaks.'
            })
    else:
        suggestions.append({
            'icon': '📝',
            'type': 'info',
            'title': 'Start Logging Activities',
            'message': 'You have no activities logged this week. Start logging to get personalized insights!'
        })
    
    # ---- 2. Best & Worst Day ----
    best_day = None
    worst_day = None
    best_score = 0
    worst_score = 11
    
    for i in range(7):
        d = week_start + datetime.timedelta(days=i)
        day_acts = Activity.objects.filter(user=request.user, date=d)
        day_avg = day_acts.aggregate(avg=Avg('productivity_score'))['avg']
        if day_avg is not None:
            if day_avg > best_score:
                best_score = day_avg
                best_day = d
            if day_avg < worst_score:
                worst_score = day_avg
                worst_day = d
    
    if best_day:
        suggestions.append({
            'icon': '🏆',
            'type': 'success',
            'title': f'Best Day: {best_day.strftime("%A")}',
            'message': f'Your most productive day this week was {best_day.strftime("%A, %b %d")} with an average score of {round(best_score, 1)}/10.'
        })
    if worst_day and worst_day != best_day:
        suggestions.append({
            'icon': '📉',
            'type': 'warning',
            'title': f'Least Productive: {worst_day.strftime("%A")}',
            'message': f'{worst_day.strftime("%A")} was your weakest day ({round(worst_score, 1)}/10). Try planning lighter tasks or taking breaks on that day.'
        })
    
    # ---- 3. Category Insights ----
    categories = {}
    for act in week_activities:
        cat = act.get_category_display()
        if cat not in categories:
            categories[cat] = {'total_score': 0, 'count': 0, 'hours': 0}
        categories[cat]['total_score'] += act.productivity_score
        categories[cat]['count'] += 1
        start = datetime.datetime.combine(act.date, act.start_time)
        end = datetime.datetime.combine(act.date, act.end_time)
        diff = (end - start).total_seconds() / 3600
        if diff > 0:
            categories[cat]['hours'] += diff
    
    # Find most time-consuming category
    if categories:
        top_cat = max(categories, key=lambda c: categories[c]['hours'])
        top_hours = round(categories[top_cat]['hours'], 1)
        suggestions.append({
            'icon': '⏰',
            'type': 'info',
            'title': f'Most Time Spent: {top_cat}',
            'message': f'You spent {top_hours} hours on "{top_cat}" this week. Make sure this aligns with your priorities.'
        })
    
    # ---- 4. Habit Insights ----
    habits = Habit.objects.filter(user=request.user)
    
    # Check for broken streaks
    for habit in habits:
        last_log = HabitLog.objects.filter(
            habit=habit, is_completed=True
        ).order_by('-date').first()
        
        if last_log:
            days_gap = (today - last_log.date).days
            if days_gap >= 3:
                suggestions.append({
                    'icon': '🔥',
                    'type': 'danger',
                    'title': f'Habit at Risk: {habit.name}',
                    'message': f'You haven\'t completed "{habit.name}" in {days_gap} days. Your streak is at risk!'
                })
        elif habit.streak == 0:
            suggestions.append({
                'icon': '💡',
                'type': 'info',
                'title': f'Get Started: {habit.name}',
                'message': f'You haven\'t started tracking "{habit.name}" yet. Complete it today to begin your streak!'
            })
    
    # Top streak
    top_habit = habits.order_by('-streak').first()
    if top_habit and top_habit.streak > 0:
        suggestions.append({
            'icon': '🎯',
            'type': 'success',
            'title': f'Top Streak: {top_habit.name}',
            'message': f'Your longest active streak is "{top_habit.name}" at {top_habit.streak} days. Don\'t break it!'
        })
    
    # ---- 5. Task Insights ----
    overdue_count = Todo.objects.filter(
        user=request.user, is_completed=False, due_date__lt=today
    ).count()
    if overdue_count > 0:
        suggestions.append({
            'icon': '🚨',
            'type': 'danger',
            'title': f'{overdue_count} Overdue Task{"s" if overdue_count > 1 else ""}',
            'message': 'You have overdue tasks. Prioritize clearing them today or reschedule the due dates.'
        })
    
    # ---- 6. Working Hours Balance ----
    total_hours = 0
    for act in week_activities:
        start = datetime.datetime.combine(act.date, act.start_time)
        end = datetime.datetime.combine(act.date, act.end_time)
        diff = (end - start).total_seconds() / 3600
        if diff > 0:
            total_hours += diff
    
    daily_avg_hours = round(total_hours / 7, 1)
    if daily_avg_hours > 10:
        suggestions.append({
            'icon': '😴',
            'type': 'warning',
            'title': 'You Might Be Overworking',
            'message': f'You\'re averaging {daily_avg_hours} hours/day this week. Make sure to rest and avoid burnout.'
        })
    elif daily_avg_hours < 2 and week_activities.exists():
        suggestions.append({
            'icon': '⏳',
            'type': 'info',
            'title': 'Low Activity Hours',
            'message': f'You\'re only averaging {daily_avg_hours} hours/day. Try to dedicate more focused time to your goals.'
        })
    
    context = {
        'suggestions': suggestions,
    }
    return render(request, 'tracker/improvement_suggestions.html', context)







