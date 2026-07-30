from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Routines
    path('routine/', views.routine_list, name='routine_list'),
    path('routine/create/', views.routine_create, name='routine_create'),
    path('routine/edit/<int:pk>/', views.routine_edit, name='routine_edit'),
    path('routine/delete/<int:pk>/', views.routine_delete, name='routine_delete'),
    path('routine/toggle/<int:pk>/', views.routine_toggle, name='routine_toggle'),

    # Activities
    path('activity/', views.activity_list, name='activity_list'),
    path('activity/log/', views.activity_create, name='activity_create'),
    path('activity/edit/<int:pk>/', views.activity_edit, name='activity_edit'),
    path('activity/delete/<int:pk>/', views.activity_delete, name='activity_delete'),

    # Habits
    path('habit/', views.habit_list, name='habit_list'),
    path('habit/add/', views.habit_create, name='habit_create'),
    path('habit/delete/<int:pk>/', views.habit_delete, name='habit_delete'),
    path('habit/toggle/<int:pk>/', views.habit_toggle, name='habit_toggle'),

    # Todos
    path('todo/', views.todo_list, name='todo_list'),
    path('todo/add/', views.todo_create, name='todo_create'),
    path('todo/edit/<int:pk>/', views.todo_edit, name='todo_edit'),
    path('todo/delete/<int:pk>/', views.todo_delete, name='todo_delete'),
    path('todo/toggle/<int:pk>/', views.todo_toggle, name='todo_toggle'),

    # Search
    path('search/', views.search_results, name='search_results'),

    # Reports
    path('report/weekly/', views.weekly_report, name='weekly_report'),
    path('report/monthly/', views.monthly_report, name='monthly_report'),

    # Habit Analysis & Insights
    path('habits/analysis/', views.habit_analysis, name='habit_analysis'),
    path('insights/', views.improvement_suggestions, name='improvement_suggestions'),
]
