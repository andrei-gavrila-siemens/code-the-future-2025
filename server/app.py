from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form.get('message')
    if message:
        # Call AI assistant to get a shape
        return jsonify({'status': 'success', 'message': 'Message received'})
    return jsonify({'status': 'error', 'message': 'No message provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)