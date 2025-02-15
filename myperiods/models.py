# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

class CycleSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    average_cycle_length = models.PositiveIntegerField(
        default=28,
        validators=[MinValueValidator(20), MaxValueValidator(45)],
        help_text="Average length of menstrual cycle in days"
    )
    average_period_length = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(2), MaxValueValidator(10)],
        help_text="Average length of period in days"
    )
    cycle_variation = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(7)],
        help_text="Typical variation in cycle length in days"
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cycle Settings for {self.user.username}"

class CycleDay(models.Model):
    FLOW_CHOICES = [
        ('NO', 'None'),
        ('LI', 'Light'),
        ('ME', 'Medium'),
        ('HE', 'Heavy'),
        ('SP', 'Spotting')
    ]

    MOOD_CHOICES = [
        ('HA', 'Happy'),
        ('SA', 'Sad'),
        ('AN', 'Angry'),
        ('AN', 'Anxious'),
        ('NE', 'Neutral')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    flow = models.CharField(max_length=2, choices=FLOW_CHOICES, blank=True, null=True)
    mood = models.CharField(max_length=2, choices=MOOD_CHOICES, blank=True, null=True)
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(35.0), MaxValueValidator(42.0)]
    )
    symptoms = models.ManyToManyField('Symptom', blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"Cycle day for {self.user.username} on {self.date}"

class Symptom(models.Model):
    CATEGORY_CHOICES = [
        ('PH', 'Physical'),
        ('EM', 'Emotional'),
        ('ME', 'Mental'),
        ('OT', 'Other')
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Cycle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    length = models.PositiveIntegerField(null=True, blank=True)
    period_length = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Cycle for {self.user.username} starting {self.start_date}"

    def save(self, *args, **kwargs):
        if self.end_date and self.start_date:
            self.length = (self.end_date - self.start_date).days
        super().save(*args, **kwargs)

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    predicted_start_date = models.DateField()
    predicted_end_date = models.DateField()
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    actual_start_date = models.DateField(null=True, blank=True)
    accuracy_days = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-predicted_start_date']

    def __str__(self):
        return f"Prediction for {self.user.username} - {self.predicted_start_date}"

    def calculate_accuracy(self):
        if self.actual_start_date:
            self.accuracy_days = abs((self.predicted_start_date - self.actual_start_date).days)
            self.save()