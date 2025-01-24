import requests
from sentence_transformers import SentenceTransformer
import faiss
import time
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def wiki_search(query: str):
    """
    Search for information about the given query using the Wikipedia API and get the full page content.
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "utf8": 1, 
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        results = response.json().get('query', {}).get('search', [])
        if results:
            top_result = results[0] 
            page_id = top_result.get('pageid')
            page_content = get_page_content(page_id)
            return {
                'info': page_content,
                'url': f"https://en.wikipedia.org/?curid={page_id}",
            }
        else:
            return {"info": "No results found", "url": "No URL found"}
    else:
        return {"error": f"HTTP error {response.status_code}"}

def get_page_content(page_id: int):
    """
    Fetch the full content of a Wikipedia page using its page ID.
    """
    content_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "pageids": page_id,
        "explaintext": 1, 
    }
    response = requests.get(content_url, params=params)
    if response.status_code == 200:
        pages = response.json().get('query', {}).get('pages', {})
        page = pages.get(str(page_id), {})
        return page.get('extract', 'No content available')
    else:
        return "Error retrieving page content."

def chunk_text(text, max_length=200):
    """
    Chunk the given text into smaller segments.
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def build_faiss_index(chunks):
    """
    Build a FAISS index from text chunks.
    """
    chunk_embeddings = embedding_model.encode(chunks)
    index = faiss.IndexFlatL2(chunk_embeddings.shape[1])  
    index.add(chunk_embeddings)
    return index, chunk_embeddings

def semantic_search(query, chunks, index):
    """
    Perform semantic search to find the most relevant chunks for the query.
    Returns the top 5 results.
    """
    query_embedding = embedding_model.encode([query])
    
    _, indices = index.search(query_embedding, k=5)
    
    return [chunks[i] for i in indices[0]]

def searcher(query : str):
    start_time = time.time()
    search_result = wiki_search(query)
    if "info" in search_result:
        #print("Original Search Result:", search_result)
        print("start searching...")
        chunks = chunk_text(search_result['info'])
        #print("\nChunks:", chunks)
        index, embeddings = build_faiss_index(chunks)
        relevant_chunk = semantic_search(query, chunks, index)
        #print("\nRelevant Chunk:", relevant_chunk)
        print('finished scanning wikipedia')
        print("--- %s wiki search ---" % (time.time() - start_time))
        return relevant_chunk
