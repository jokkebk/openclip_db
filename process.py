import torch, sys, os
import numpy as np
from PIL import Image
import open_clip

from db import ImageEmbeddings, get_session

if len(sys.argv) < 2:
    print("Usage: python process.py <images>")
    exit(1)

image_files = []
for arg in sys.argv[1:]:
    full_path = os.path.abspath(arg)
    # If it is a file, add full path to image_files
    if os.path.isfile(arg):
        image_files.append(full_path)
    # If it is a directory, add all image files in directory to image_files
    elif os.path.isdir(arg):
        # Walk through directory and add all image files to image_files
        for root, dirs, files in os.walk(full_path):
            for f in files:
                if f.endswith(".jpg") or f.endswith(".jpeg") or f.endswith(".png"):
                    image_files.append(os.path.join(root, f))
    else: # If it is neither a file nor a directory, print error message and exit
        print("Error: {} is neither a file nor a directory".format(arg))
        exit(1)
    
session = get_session('images.db')

# Get all image filenames from database
image_filenames = session.query(ImageEmbeddings.filename).all()
image_filenames = [f[0] for f in image_filenames]

# Remove images that are already in the database
image_files = [f for f in image_files if f not in image_filenames]

if len(image_files) == 0:
    print("No new images to process")
    exit(0)

print(len(image_files), "images not in database") #, *image_files, sep='\n')

#model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
#tokenizer = open_clip.get_tokenizer('ViT-B-32')
model, _, preprocess = open_clip.create_model_and_transforms('ViT-H-14', pretrained='laion2b_s32b_b79k')
tokenizer = open_clip.get_tokenizer('ViT-H-14')

image_files = np.array(image_files)

batch_size = 8

for i in range(0, len(image_files), batch_size):
    batch = image_files[i:i+batch_size]
    print(i, batch)
    
    images = []
    paths = []
    # Try to open and preprocess images
    for f in batch:
        try:
            img = preprocess(Image.open(f)).unsqueeze(0)
            images.append(img)
            paths.append(f)
        except:
            print("Error: could not open", f)

    if len(images) == 0: continue # if all failed, next

    images = torch.cat(images)
    with torch.no_grad(), torch.cuda.amp.autocast():
        image_features = model.encode_image(images)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        # Store image features in database, convert to numpy array first
        image_features = image_features.cpu().numpy()
        session.bulk_save_objects([ImageEmbeddings(filename=f, embedding=embedding) for f, embedding in zip(paths, image_features)])
        session.commit()
