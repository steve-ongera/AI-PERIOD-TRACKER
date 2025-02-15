# admin.py
from django.contrib import admin
from .models import CycleSetting, CycleDay, Symptom, Cycle, Prediction

@admin.register(CycleSetting)
class CycleSettingAdmin(admin.ModelAdmin):
    list_display = ['user', 'average_cycle_length', 'average_period_length', 'last_updated']
    search_fields = ['user__username']

@admin.register(CycleDay)
class CycleDayAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'flow', 'mood', 'temperature']
    list_filter = ['flow', 'mood', 'date']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'date'

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']

@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'end_date', 'length', 'period_length']
    list_filter = ['start_date']
    search_fields = ['user__username', 'notes']
    date_hierarchy = 'start_date'

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['user', 'predicted_start_date', 'confidence_score', 'accuracy_days']
    list_filter = ['predicted_start_date', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'predicted_start_date'