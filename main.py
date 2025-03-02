from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI()

# Request Model for Updating Rating
class RatingUpdateRequest(BaseModel):
    winner_rating: float
    loser_rating: float
    score_diff: int
    winner_past_opponents: list[float] = []  # Ratings of past opponents of winner
    loser_past_opponents: list[float] = []  # Ratings of past opponents of loser

# Request Model for Match Prediction
class MatchPredictionRequest(BaseModel):
    player1_rating: float
    player2_rating: float

# Request Model for Unplayed Match Prediction
class UnplayedMatchRequest(BaseModel):
    player1_rating: float
    player2_rating: float
    mutual_opponents_ratings: list[float] = []  # Ratings of mutual opponents

# 1️ Match Outcome Prediction
@app.post("/predict-outcome/")
def predict_match_outcome(request: MatchPredictionRequest):
    probability = 1 / (1 + 10 ** ((request.player2_rating - request.player1_rating) / 50))
    return {
        "player1_win_probability": probability,
        "player2_win_probability": 1 - probability
    }

# 2️ Dynamic Rating Adjustment (Bayesian Elo + Graph Influence)
@app.post("/update-rating/")
def update_rating(request: RatingUpdateRequest):
    K = 5  # Base K-factor
    margin_factor = 1 + (request.score_diff / 6)  # Adjust based on match margin

    expected_win = 1 / (1 + 10 ** ((request.loser_rating - request.winner_rating) / 50))
    rating_change = K * margin_factor * (1 - expected_win)

    winner_new_rating = max(3, request.winner_rating + rating_change)
    loser_new_rating = max(3, request.loser_rating - rating_change)

    # Adjust ratings for past opponents (indirect influence)
    def adjust_opponents_ratings(opponent_ratings, is_winner):
        adjusted_ratings = []
        dampening_factor = 0.1  # Reduces influence over indirect matches
        for rating in opponent_ratings:
            adjustment = rating_change * dampening_factor if is_winner else -rating_change * dampening_factor
            adjusted_ratings.append(round(max(3, rating + adjustment), 2))
        return adjusted_ratings

    winner_past_opponents_updated = adjust_opponents_ratings(request.winner_past_opponents, True)
    loser_past_opponents_updated = adjust_opponents_ratings(request.loser_past_opponents, False)

    return {
        "winner_new_rating": round(winner_new_rating, 2),
        "loser_new_rating": round(loser_new_rating, 2),
        "winner_past_opponents_updated": winner_past_opponents_updated,
        "loser_past_opponents_updated": loser_past_opponents_updated
    }

# 3️ Unplayed Match Rating Estimation (Graph-Based Influence)
@app.post("/predict-unplayed-match/")
def predict_unplayed_match(request: UnplayedMatchRequest):
    if request.mutual_opponents_ratings:
        avg_opponent_rating = sum(request.mutual_opponents_ratings) / len(request.mutual_opponents_ratings)
        estimated_rating_diff = ((request.player1_rating - request.player2_rating) + avg_opponent_rating) / 2
    else:
        estimated_rating_diff = (request.player1_rating - request.player2_rating) / 2
    
    return {"estimated_rating_diff": round(estimated_rating_diff, 2)}
