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
img.result {
  max-width: 256px;
  max-height: 256px;
}
</style>
<!-- <main> -->
<h1>OpenCLIP DB Svelte GUI</h1>

<p>
  Query: <input id="query" bind:value={query} />
<button on:click={search}>Search</button>
</p>

{#if results.length > 0}
  <ul>
    {#each results as r}
      <li>#{r.id}: Score {r.score}
      <img class="result" src={`${endpoint}/api/image/${r.id}`} alt={r.filename}/>
      </li>
    {/each}
  </ul>
{:else}
  <p>No results</p>
{/if}
