# OpenCLIP DB with Python / Svelte web query interface

## process.py

Extracts embeddings for images using the OpenCLIP model and stores them in a SQLite database.

Pre-requisite libraries:

    torch, numpy, Pillow, open_clip.

### Installation

```bash
$ pip install torch open_clip numpy Pillow
```

### Usage

You can provide multiple image paths and/or directories. Only .jpg, .jpeg, and .png formats are considered.

```bash
$ python process.py <path_to_image_or_directory>...
```

### Functionality

1. Gathers specified image paths.
2. Connects to the images.db SQLite database.
3. Filters out already processed images.
4. Generates and normalizes OpenCLIP embeddings (ViT-H-14 variant).
5. Stores embeddings in the database.

## Svelte web query interface

Provides a web interface for querying the OpenCLIP database. Resides in `svelte-ui` subfolder.

### Installation

```bash
$ cd svelte-ui
$ npm install
```

### Usage

You can either run the development server or build the static files.

```bash
$ npm run dev
```

```bash
$ npm run build
```

For the latter to work with `server.py`, you need to symlink (or copy) the
`svelte-ui/dist` folder to the `static` folder.

```bash
$ ln -s svelte-ui/dist static
```

## server.py

Provides a web interface for querying the OpenCLIP database.

Pre-requisite libraries (in addition to those of `process.py`):

    flask, flask_cors
    
### Installation

```bash
$ pip install flask flask_cors
```

### Usage

```bash
$ python server.py
```

For the server to be of any use, you first need to use `process.py` to populate the database.