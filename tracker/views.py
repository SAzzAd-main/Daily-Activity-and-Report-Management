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




