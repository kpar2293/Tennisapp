from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RatingUpdateRequest(BaseModel):
    winner_rating: float
    loser_rating: float
    score_diff: int

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
async def update_rating(data: RatingUpdateRequest):
    winner_new_rating = data.winner_rating + (data.score_diff * 0.1)  # Example update logic
    loser_new_rating = data.loser_rating - (data.score_diff * 0.1)

    return {
        "winner_new_rating": round(winner_new_rating, 2),
        "loser_new_rating": round(loser_new_rating, 2)
    }

# Endpoint for unplayed match predictions (Step 3)
@app.post("/predict-unplayed/")
def predict_unplayed(player1_rating: float, player2_rating: float):
    estimated_rating_diff = (player1_rating - player2_rating) / 2  # Simple estimation
    return {"estimated_rating_diff": estimated_rating_diff}
