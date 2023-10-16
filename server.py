"""Simple Flask server to serve the web app.

    The server will provide files in static/ folder by default,
    and additionally have /api/ endpoints for the web app to
    fetch data from the database."""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

# Alternatively, to accept CORS requests from any origin,
# one could use the following in each route:
#response.headers.add('Access-Control-Allow-Origin', '*')

from db import ImageEmbeddings, get_session

session = get_session('images.db')

# Fetch all image embeddings from database along with their filenames and ids
data = session.query(ImageEmbeddings.id, ImageEmbeddings.filename, ImageEmbeddings.embedding).all()

import numpy as np

# Create np.array of embeddings
embeddings = np.array([d[2] for d in data])

# Discard the embeddings from the data to save some memory
data = [(d[0], d[1]) for d in data]

# Show how much memory the embeddings take up
print(len(embeddings), "embeddings take up", embeddings.nbytes / 1024 / 1024, "MB")

import torch, open_clip
from PIL import Image

model, _, preprocess = open_clip.create_model_and_transforms('ViT-H-14', pretrained='laion2b_s32b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-H-14')

# Serve the static Svelte app
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

@app.route('/api/search', methods=['GET', 'POST'])
def search():
    """Search for images similar to the query string or uploaded image."""
    # Additional results parameter to return the top N results
    top_n = request.form.get('results', 100)
   
    # Check if the request is a POST request with an image
    if request.method == 'POST' and 'image' in request.files:
        # Load posted image
        image = Image.open(request.files['image'])
        print('Received image with dimensions', image.size)

        # Preprocess image and add batch dimension
        image = preprocess(image).unsqueeze(0)

        # Pass image through model
        with torch.no_grad(), torch.cuda.amp.autocast():
            features = model.encode_image(image)
            # Normalize, though it isn't strictly necessary
            features /= features.norm(dim=-1, keepdim=True)
    else:
        query_string = request.args.get('q', '')
    
        with torch.no_grad(), torch.cuda.amp.autocast():
            text = tokenizer(query_string)
            features = model.encode_text(text)
            # Normalize, though it isn't strictly necessary
            features /= features.norm(dim=-1, keepdim=True)

    # Calculate cosine similarity between query embedding and all embeddings
    scores = features @ embeddings.T
    
    # Convert to Python list
    scores = scores.squeeze().cpu().numpy().tolist()

    # Sort the entries by score
    sorted_entries = sorted(zip(scores, data), reverse=True)

    # Return the top N entries
    results = []
    for score, (id, filename) in sorted_entries[:top_n]:
        results.append({
            'id': id,
            'filename': filename,
            'score': float(score),
        })

    response = jsonify({'results': results})

    return response
    
@app.route('/api/image/<int:id>', methods=['GET'])
def image(id):
    """Return the image with the given id."""
    # Get the filename of the image with the given id from data
    filename = next((d[1] for d in data if int(d[0]) == id), None)
    if filename is None:
        return jsonify({'error': 'Image not found'}), 404

    # Return the image file
    return send_file(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
