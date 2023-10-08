"""Simple Flask server to serve the web app.

    The server will provide files in static/ folder by default,
    and additionally have /api/ endpoints for the web app to
    fetch data from the database."""

from flask import Flask, request, jsonify, send_from_directory

# Serve the static Svelte app
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

# JSON API for fetching news articles
@app.route('/api/search', methods=['GET'])
def search():
    query_string = request.args.get('query', '')

    # Create embedding for query string
    query_embedding = model.encode(query_string)

    # Calculate cosine similarity between query embedding and all embeddings
    scores = query_embedding @ embeddings.T

    # Sort the entries by score
    sorted_entries = sorted(zip(scores, entries), reverse=True)

    # Return the top 10 entries
    results = []
    for score, entry in sorted_entries[:10]:
        results.append({
            'title': entry.title,
            'content': entry.summary,
            'url': entry.url,
            'published_date': entry.published_date.isoformat(),
            'score': float(score),
            'read': entry.read,
            'rating': entry.rating,
        })

    return jsonify({'entries': results})

if __name__ == '__main__':
    app.run(debug=True)