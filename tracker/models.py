from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Routine(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    
    CATEGORY_CHOICES = [
        ('WORK', 'Work'),
        ('HEALTH', 'Health'),
        ('EDUCATION', 'Education'),
        ('LEISURE', 'Leisure'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"


class Activity(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
    ]
    
    CATEGORY_CHOICES = [
        ('WORK', 'Work'),
        ('HEALTH', 'Health'),
        ('EDUCATION', 'Education'),
        ('LEISURE', 'Leisure'),
        ('SOCIAL_MEDIA', 'Social Media'),
        ('WASTED', 'Wasted Time'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='COMPLETED')
    mood = models.CharField(max_length=50, blank=True, help_text="e.g. Happy, Focused, Tired")
    productivity_score = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rate from 1 (lowest) to 10 (highest)"
    )

    def __str__(self):
        return f"{self.title} on {self.date}"


class Habit(models.Model):
    HABIT_TYPE_CHOICES = [
        ('GOOD', 'Good Habit'),
        ('BAD', 'Bad Habit'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    habit_type = models.CharField(max_length=10, choices=HABIT_TYPE_CHOICES, default='GOOD')
    streak = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_habit_type_display()})"


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('habit', 'date')

    def __str__(self):
        status = "Completed" if self.is_completed else "Missed/Triggered"
        return f"{self.habit.name} on {self.date} - {status}"


class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
