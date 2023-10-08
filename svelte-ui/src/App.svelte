<script>
  let query = '';
  let results = [];
  
  const endpoint = 'http://localhost:5000';

  function search() {
    console.log(query);
    // Run a search query against endpoint's /api/search
    fetch(`${endpoint}/api/search?q=${query}`)
      .then(response => response.json())
      .then(data => {
        console.log(data);
        // Return results if there are any
        if (data.results) results = data.results;
      });
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
</style>
<!-- <main> -->
<h1>OpenCLIP DB Svelte GUI</h1>

<p>
  Query: <input id="query" bind:value={query} />
<button on:click={search}>Search</button>
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