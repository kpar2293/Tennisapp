from fastapi import FastAPI
from pydantic import BaseModel
import math
import networkx as nx

app = FastAPI()

# Graph to track matches and ratings
player_graph = nx.DiGraph()  # Directed graph for match outcomes

# Request Model for Rating Update
class RatingUpdateRequest(BaseModel):
    winner: str
    loser: str
    score_diff: int
    winner_rating: float
    loser_rating: float

# Request Model for Unplayed Match Prediction
class UnplayedMatchRequest(BaseModel):
    player1: str
    player2: str

# Function to update ratings and propagate influence
@app.post("/update-rating/")
def update_rating(request: RatingUpdateRequest):
    K = 5  # Base K-factor

    # ✅ Corrected Math functions
    expected_margin = 2 + 0.5 * math.fabs(request.loser_rating - request.winner_rating)
    margin_factor = 1 + math.log((request.score_diff + 1) / (expected_margin + 1))

    expected_win = 1 / (1 + 10 ** ((request.loser_rating - request.winner_rating) / 50))
    rating_change = K * margin_factor * (1 - expected_win)

    winner_new_rating = max(3, request.winner_rating + rating_change)
    loser_new_rating = max(3, request.loser_rating - rating_change)

    # ✅ Corrected Graph Node Checking
    if not player_graph.has_node(request.winner):
        player_graph.add_node(request.winner, rating=winner_new_rating)
    else:
        player_graph.nodes[request.winner]["rating"] = winner_new_rating  # Update rating

    if not player_graph.has_node(request.loser):
        player_graph.add_node(request.loser, rating=loser_new_rating)
    else:
        player_graph.nodes[request.loser]["rating"] = loser_new_rating  # Update rating

    # ✅ Corrected Edge Addition
    player_graph.add_edge(request.winner, request.loser, weight=rating_change)

    # Adjust past opponents (Graph Influence)
    dampening_factor = 0.1  
    for neighbor in player_graph.predecessors(request.loser):  # Players who lost to the loser
        if player_graph.has_node(neighbor):  # Ensure the node exists
            old_rating = player_graph.nodes[neighbor]["rating"]
            player_graph.nodes[neighbor]["rating"] = max(3, old_rating - rating_change * dampening_factor)

    return {
        "winner_new_rating": round(winner_new_rating, 2),
        "loser_new_rating": round(loser_new_rating, 2),
    }

# Predict unplayed match using mutual opponents
@app.post("/predict-unplayed-match/")
def predict_unplayed_match(request: UnplayedMatchRequest):
    if not player_graph.has_node(request.player1) or not player_graph.has_node(request.player2):
        return {"error": "One or both players not found in the system"}

    mutual_opponents = list(set(player_graph.predecessors(request.player1)) & set(player_graph.predecessors(request.player2)))

    if mutual_opponents:
        avg_opponent_rating = sum(player_graph.nodes[p]["rating"] for p in mutual_opponents) / len(mutual_opponents)
        estimated_rating_diff = ((player_graph.nodes[request.player1]["rating"] - player_graph.nodes[request.player2]["rating"]) + avg_opponent_rating) / 2
    else:
        estimated_rating_diff = (player_graph.nodes[request.player1]["rating"] - player_graph.nodes[request.player2]["rating"]) / 2
    
    return {"estimated_rating_diff": round(estimated_rating_diff, 2)}
