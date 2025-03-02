from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI()

# Request Model for Updating Rating
class RatingUpdateRequest(BaseModel):
    winner_rating: float
    loser_rating: float
    score_diff: int

# Request Model for Match Prediction
class MatchPredictionRequest(BaseModel):
    player1_rating: float
    player2_rating: float

# Request Model for Unplayed Match Prediction
class UnplayedMatchRequest(BaseModel):
    player1_rating: float
    player2_rating: float

# 1️ Match Outcome Prediction
@app.post("/predict-outcome/")
def predict_match_outcome(request: MatchPredictionRequest):
    probability = 1 / (1 + 10 ** ((request.player2_rating - request.player1_rating) / 50))
    return {
        "player1_win_probability": probability,
        "player2_win_probability": 1 - probability
    }

# 2️ Dynamic Rating Adjustment (Bayesian Elo)
@app.post("/update-rating/")
def update_rating(request: RatingUpdateRequest):
    K = 5  # Base K-factor
    margin_factor = 1 + (request.score_diff / 6)  # Adjust based on match margin

    expected_win = 1 / (1 + 10 ** ((request.loser_rating - request.winner_rating) / 50))
    rating_change = K * margin_factor * (1 - expected_win)

    winner_new_rating = max(3, request.winner_rating + rating_change)
    loser_new_rating = max(3, request.loser_rating - rating_change)

    return {
        "winner_new_rating": round(winner_new_rating, 2),
        "loser_new_rating": round(loser_new_rating, 2)
    }

# 3️ Unplayed Match Rating Estimation
@app.post("/predict-unplayed-match/")
def predict_unplayed_match(request: UnplayedMatchRequest):
    estimated_rating_diff = (request.player1_rating - request.player2_rating) / 2
    return {"estimated_rating_diff": estimated_rating_diff}
