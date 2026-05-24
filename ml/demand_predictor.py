"""
ml/demand_predictor.py – Booking demand prediction model stub.
Phase 3 – Data Science Integration.

Will use: scikit-learn, pandas, numpy
"""

# Future implementation outline:
# 1. Feature engineering from historical bookings:
#    - Day of week, month, season
#    - Lead time (days between booking and check-in)
#    - Hotel rating, room type, price
# 2. Model: RandomForestRegressor or XGBoost
# 3. Target: Number of bookings per day
# 4. Output: Heatmap of predicted demand by date

class DemandPredictor:
    """Predicts daily booking demand for a given hotel."""

    def __init__(self, hotel_id: int):
        self.hotel_id = hotel_id
        self.model = None

    def train(self, df):
        """
        Train the demand model.
        :param df: pandas DataFrame with booking history
        """
        raise NotImplementedError("Phase 3 – Coming soon")

    def predict(self, future_dates):
        """
        Predict demand for a list of future dates.
        :param future_dates: list of datetime objects
        :return: list of predicted booking counts
        """
        raise NotImplementedError("Phase 3 – Coming soon")
