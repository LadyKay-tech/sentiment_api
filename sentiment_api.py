from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from textblob import TextBlob
from flask_limiter.util import get_remote_address


app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379", default_limits=["1000 per day", "100 per hour"])
limiter.init_app(app)

@app.route('/sentiment', methods=['POST'])
@limiter.limit('10/hour')
def sentiment_analysis():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            abort(400, description="Bad Request: Missing 'text' parameter in the request body.")
        
        text = data['text']
        if len(text) > 1000:
            abort(400, description="Bad Request: 'text' parameter should not exceed 1000 characters.")
        
        sentiment = TextBlob(text).sentiment.polarity
        result = {'sentiment': 'positive' if sentiment > 0 else 'negative' if sentiment < 0 else 'neutral'}
        return jsonify(result)
    except Exception as e:
        abort(500, description=str(e))

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': error.description}), 400

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': error.description}), 500

if __name__ == '__main__':
    app.run(debug=True)
