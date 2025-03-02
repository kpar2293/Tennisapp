from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Tennis Rating API is running"}

# Endpoint for match outcome prediction (Step 1)
@app.post("/predict-outcome/")
def predict_outcome(player1_rating: float, player2_rating: float):
    probability = 1 / (1 + 10 ** ((player2_rating - player1_rating) / 50))
    return {"player1_win_probability": probability, "player2_win_probability": 1 - probability}

# Endpoint for rating adjustments (Step 2)
@app.post("/update-rating/")
def update_rating(winner_rating: float, loser_rating: float, score_diff: int):
    K = 5
    margin_factor = 1 + (score_diff / 6)  # Example margin impact
    expected_win = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 50))
    rating_change = K * margin_factor * (1 - expected_win)

    winner_new_rating = max(3, winner_rating + rating_change)
    loser_new_rating = max(3, loser_rating - rating_change)

    return {"winner_new_rating": winner_new_rating, "loser_new_rating": loser_new_rating}

# Endpoint for unplayed match predictions (Step 3)
@app.post("/predict-unplayed/")
def predict_unplayed(player1_rating: float, player2_rating: float):
    estimated_rating_diff = (player1_rating - player2_rating) / 2  # Simple estimation
    return {"estimated_rating_diff": estimated_rating_diff}
