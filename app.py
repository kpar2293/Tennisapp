from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/update_rating', methods=['POST'])
def update_rating():
    data = request.json
    # Process the match data and update ratings
    return jsonify({"message": "Ratings updated!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
