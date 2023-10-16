<script>
  let query = '';
  let results = [];
  let imageFile = null;
  
  const endpoint = 'http://localhost:5000';

  async function search() {
    console.log(query);
    try {
      // Run a search query against endpoint's /api/search
      const response = await fetch(`${endpoint}/api/search?q=${query}`);
      const data = await response.json();
      console.log(data);
      // Return results if there are any
      if (data.results) results = data.results;
    } catch (error) {
      console.error(error);
    }
  }

  async function searchImage() {
    if (!imageFile) return;
    try {
      // Create a FormData object and append the image
      const formData = new FormData();
      formData.append('image', imageFile);
      
      // Send the image data to the server to search for similar images
      const response = await fetch(`${endpoint}/api/search`, {
        method: 'POST',
        body: formData // No need to specify content-type; fetch does it for you
      });
      const data = await response.json();
      console.log(data);
      // Return results if there are any
      if (data.results) results = data.results;
    } catch (error) {
      console.error(error);
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file.type.startsWith('image/')) {
      imageFile = file;
      searchImage();
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
  }

  function handleFileInput(event) {
    imageFile = event.target.files[0];
  }
</script>

<style>
/* Limit image size to 256x256 */
.results img {
  max-width: 256px;
  max-height: 256px;
}

/* No border on buttons */
.results button {
  border: none;
}

/* Apply larger size to images with the 'enlarged' class */
img.enlarged {
  max-width: 100% !important;
  max-height: 100% !important;
}

/* Image upload area */
.drop-area {
  border: 2px dashed #ccc;
  padding: 20px;
  margin-bottom: 20px;
}
</style>
<!-- <main> -->
<h1>OpenCLIP DB Svelte GUI</h1>

<p>
  <!-- image upload -->
  <label for="image">Upload an image:</label>
  <input type="file" id="image" on:change={handleFileInput} />
  <button on:click={searchImage}>Search</button>
</p>

<div class="drop-area" on:drop={handleDrop} on:dragover={handleDragOver}
role="region" aria-label="Image upload area">
  <p>Drag and drop an image here to search for similar images</p>
</div>

<p>
  Image: <input type="file" id="image" />
<button on:click={searchImage}>Search</button>
</p>

{#if results.length > 0}
  <ul class="results">
    {#each results as r}
      <li>#{r.id}: Score {r.score}
        <button on:click={() => { r.enlarged = !r.enlarged }}>
          <img class:enlarged={r.enlarged} src={`${endpoint}/api/image/${r.id}`} alt={r.filename}/>
        </button>
      </li>
    {/each}
  </ul>
{:else}
  <p>No results</p>
{/if}
