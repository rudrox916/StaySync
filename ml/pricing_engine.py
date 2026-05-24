"""
ml/pricing_engine.py – Dynamic pricing model stub.
Phase 3 – Data Science Integration.
"""

class DynamicPricingEngine:
    """
    Adjusts room prices based on:
    - Predicted occupancy / demand
    - Seasonality
    - Lead time
    - Day of week
    """

    BASE_MULTIPLIERS = {
        'high_demand': 1.4,
        'normal':      1.0,
        'low_demand':  0.85,
    }

    def suggest_price(self, base_price: float, occupancy_rate: float,
                      days_until_checkin: int) -> float:
        """
        Return a suggested price for a room.
        Phase 3 will replace this with an ML model.
        """
        # Simple rule-based placeholder
        if occupancy_rate > 0.8 or days_until_checkin <= 3:
            return round(base_price * self.BASE_MULTIPLIERS['high_demand'], 2)
        elif occupancy_rate < 0.3:
            return round(base_price * self.BASE_MULTIPLIERS['low_demand'], 2)
        return round(base_price * self.BASE_MULTIPLIERS['normal'], 2)
