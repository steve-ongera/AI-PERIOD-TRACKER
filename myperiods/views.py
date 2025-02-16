# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from .models import CycleDay, CycleSetting, Cycle, Prediction
from .forms import UserRegistrationForm, CycleSettingForm, CycleDayForm
from .services import CyclePredictionService
from django.db.models import Avg


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'cycle_tracker/register.html', {'form': form})

@login_required
def dashboard(request):
    today = datetime.now().date()
    cycle_service = CyclePredictionService(request.user)
    
    context = {
        'today_entry': CycleDay.objects.filter(user=request.user, date=today).first(),
        'current_cycle': Cycle.objects.filter(user=request.user).first(),
        'latest_prediction': Prediction.objects.filter(user=request.user).first(),
        'recent_days': CycleDay.objects.filter(user=request.user).order_by('-date')[:7],
        'settings': CycleSetting.objects.get_or_create(user=request.user)[0],
    }
    
    return render(request, 'cycle_tracker/dashboard.html', context)

class CycleDayCreate(LoginRequiredMixin, CreateView):
    model = CycleDay
    form_class = CycleDayForm
    template_name = 'cycle_tracker/cycleday_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CycleDayUpdate(LoginRequiredMixin, UpdateView):
    model = CycleDay
    form_class = CycleDayForm
    template_name = 'cycle_tracker/cycleday_form.html'
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return CycleDay.objects.filter(user=self.request.user)

@login_required
def calendar_view(request):
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    end_date = today + timedelta(days=60)
    
    cycle_days = CycleDay.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )
    
    predictions = Prediction.objects.filter(
        user=request.user,
        predicted_start_date__range=[start_date, end_date]
    )
    
    context = {
        'cycle_days': cycle_days,
        'predictions': predictions,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'calender/calendar.html', context)


@login_required
def settings_view(request):
    settings = get_object_or_404(CycleSetting, user=request.user)
    
    if request.method == 'POST':
        form = CycleSettingForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('dashboard')
    else:
        form = CycleSettingForm(instance=settings)
    
    return render(request, 'cycle_tracker/settings.html', {'form': form})

@login_required
def stats_view(request):
    cycles = Cycle.objects.filter(user=request.user).order_by('-start_date')[:12]
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')[:12]
    
    context = {
        'cycles': cycles,
        'predictions': predictions,
        'avg_cycle_length': cycles.aggregate(Avg('length'))['length__avg'],
        'avg_prediction_accuracy': predictions.aggregate(Avg('accuracy_days'))['accuracy_days__avg'],
    }
    
    return render(request, 'cycle_tracker/stats.html', context)

