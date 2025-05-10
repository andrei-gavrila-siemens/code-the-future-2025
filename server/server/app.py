from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form.get('message')
    if not message:
        return jsonify({'status': 'error', 'message': 'No message provided'}), 400
    
    # Convert the message to lowercase to make the check case-insensitive
    message = message.lower()
    
    # Check for shape keywords
    if 'house' in message:
        return jsonify({
            "size_x": 1,
            "size_y": 2,
            "blocks": [
                {"type": "square", "x": 0, "y": 0},
                {"type": "triangle", "x": 0, "y": 1}
            ]
        })
    elif 'tower' in message:
        return jsonify({
            "size_x": 1,
            "size_y": 4,
            "blocks": [
                {"type": "square", "x": 0, "y": 0},
                {"type": "square", "x": 0, "y": 1},
                {"type": "square", "x": 0, "y": 2},
                {"type": "square", "x": 0, "y": 3}
            ]
        })
    elif 'village' in message:
        return jsonify({
            "size_x": 5,
            "size_y": 3,
            "blocks": [
                # First house
                {"type": "square", "x": 0, "y": 0},
                {"type": "triangle", "x": 0, "y": 1},
                
                # Second house
                {"type": "square", "x": 2, "y": 0},
                {"type": "triangle", "x": 2, "y": 1},
                
                # Tower
                {"type": "square", "x": 4, "y": 0},
                {"type": "square", "x": 4, "y": 1},
                {"type": "square", "x": 4, "y": 2}
            ]
        })
    else:
        # Return a consistent error response for unrecognized shapes
        # The funny response is handled client-side
        return jsonify({'status': 'error', 'message': 'No recognized shape in the prompt'}), 400

if __name__ == '__main__':
    app.run(debug=True)