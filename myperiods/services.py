# services.py
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from .models import Cycle, Prediction, CycleSetting

class CyclePredictionService:
    def __init__(self, user):
        self.user = user
        self.settings = CycleSetting.objects.get_or_create(user=user)[0]
        self.cycles = Cycle.objects.filter(user=user).order_by('-start_date')
        
    def get_cycle_lengths(self, limit=6):
        """Get the lengths of the last n cycles"""
        return [cycle.length for cycle in self.cycles[:limit] if cycle.length]
    
    def calculate_basic_prediction(self):
        """Calculate prediction based on average cycle length"""
        last_cycle = self.cycles.first()
        if not last_cycle:
            return None
            
        cycle_lengths = self.get_cycle_lengths()
        if cycle_lengths:
            avg_length = np.mean(cycle_lengths)
            std_dev = np.std(cycle_lengths)
        else:
            avg_length = self.settings.average_cycle_length
            std_dev = self.settings.cycle_variation
            
        predicted_start = last_cycle.start_date + timedelta(days=int(avg_length))
        predicted_end = predicted_start + timedelta(days=self.settings.average_period_length)
        
        # Calculate confidence score based on standard deviation
        confidence_score = 1.0 / (1.0 + std_dev / avg_length)
        
        return {
            'predicted_start_date': predicted_start,
            'predicted_end_date': predicted_end,
            'confidence_score': confidence_score
        }
    
    def calculate_advanced_prediction(self):
        """Calculate prediction using linear regression on historical data"""
        if self.cycles.count() < 3:
            return self.calculate_basic_prediction()
            
        # Prepare data for linear regression
        cycle_data = self.cycles.values_list('start_date', 'length')
        dates = [(d[0] - cycle_data[0][0]).days for d in cycle_data]
        lengths = [d[1] for d in cycle_data if d[1]]
        
        if len(dates) < 3:
            return self.calculate_basic_prediction()
            
        # Reshape data for sklearn
        X = np.array(dates[1:]).reshape(-1, 1)
        y = np.array(lengths[:-1])
        
        # Fit linear regression model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next cycle length
        next_date = len(dates)
        predicted_length = model.predict([[next_date]])[0]
        
        # Calculate prediction
        last_cycle = self.cycles.first()
        predicted_start = last_cycle.start_date + timedelta(days=int(predicted_length))
        predicted_end = predicted_start + timedelta(days=self.settings.average_period_length)
        
        # Calculate confidence score based on R² score
        confidence_score = max(0.5, min(1.0, model.score(X, y)))
        
        return {
            'predicted_start_date': predicted_start,
            'predicted_end_date': predicted_end,
            'confidence_score': confidence_score
        }
    
    def create_prediction(self):
        """Create a new prediction for the user"""
        prediction_data = (
            self.calculate_advanced_prediction() 
            if self.cycles.count() >= 3 
            else self.calculate_basic_prediction()
        )
        
        if prediction_data:
            return Prediction.objects.create(
                user=self.user,
                **prediction_data
            )
        return None