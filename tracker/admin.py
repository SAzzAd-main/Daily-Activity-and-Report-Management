from django.contrib import admin
from .models import Routine, Activity, Habit, HabitLog, Todo

@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'start_time', 'end_time', 'is_completed']
    list_filter = ['category', 'priority', 'is_completed', 'user']
    search_fields = ['title', 'user__username']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'date', 'start_time', 'end_time', 'status', 'productivity_score']
    list_filter = ['category', 'status', 'date', 'user']
    search_fields = ['title', 'description', 'user__username']


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'habit_type', 'streak', 'created_at']
    list_filter = ['habit_type', 'user']
    search_fields = ['name', 'user__username']


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    list_display = ['habit', 'date', 'is_completed']
    list_filter = ['date', 'is_completed', 'habit__user']
    search_fields = ['habit__name', 'habit__user__username']


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'is_completed', 'due_date']
    list_filter = ['priority', 'is_completed', 'due_date', 'user']
    search_fields = ['title', 'user__username']

