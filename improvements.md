# Improvements.md

## hybrid_chat.py

### **Bugs Fixed**

1. **Fixed deprecated / v2-incompatible Pinecone calls**

   * **Why:** The previous Pinecone client syntax was outdated and incompatible with the latest v2 API. Updating these calls ensured that vector operations such as querying and indexing work correctly under the new client architecture.
2. **Removed unused import (`json`)**

   * **Why:** This import was unnecessary and led to minor clutter. Cleaning up unused dependencies improves readability and maintainability.

---

### **Improvements**

1. **Changed `Embed_Model` from `text-embedding-3-small` to `all-MiniLM-L6-v2`**

   * **Reasoning:**

     * OpenAI embeddings require paid access, whereas `all-MiniLM-L6-v2` (from `sentence-transformers`) provides high-quality, cost-free embeddings suitable for semantic similarity and retrieval.
     * It also ensures better local performance and no API dependency.

2. **Replaced OpenAI imports with Groq API integration**

   * **Reasoning:**

     * Groq’s local-first API access allows using open LLMs like LLaMA without incurring OpenAI usage costs.
     * Improves flexibility and makes the project viable for local or offline inference setups.

3. **Changed model from `gpt-4o-mini` to `llama-3.3-70b-versatile`**

   * **Reasoning:**

     * LLaMA 3.3 (70B) offers strong performance and context understanding, matching GPT-4-class capabilities without depending on OpenAI keys.
     * This improves accessibility for open-source and free deployments.

4. **Improved prompt clarity and Neo4j query coherence**

   * **Reasoning:**

     * Refined the prompt to provide the LLM with clearer context from both Pinecone (vector retrieval) and Neo4j (graph knowledge).
     * This ensures more structured and contextually aware responses.

5. **Added chain-of-thought style reasoning**

   * **Reasoning:**

     * Encourages the LLM to reason step-by-step internally before producing final answers, improving factual accuracy and coherence, especially for multi-day travel planning or complex relational queries.

6. **Integrated `search_summary()` to summarize top nodes**

   * **Reasoning:**

     * Centralizes retrieval and summarization logic for Pinecone and Neo4j.
     * Simplifies debugging and maintains modularity, improving code clarity and reuse.

---

### **Thought Process**

The goal was to **replace all paid or deprecated dependencies with free, stable, and modern equivalents** while improving the user query pipeline.

* Pinecone and Neo4j were maintained as hybrid retrieval systems for structured + unstructured knowledge integration.
* The embedding and chat model changes optimize cost and performance without losing accuracy.
* The design now encourages reasoning transparency and future scalability.

---

## pinecone_upload.py

### **Bugs Fixed**

1. **Updated deprecated Pinecone list index method**

   * Changed from `pc.list_indexes().names()` to `[index.name for index in pc.list_indexes()]`.
   * **Reasoning:** Required for Pinecone’s latest Python client (v2) which changed method signatures. Ensures index checks work as intended.

2. **Added `model` parameter to `get_embeddings()` call**

   * **Reasoning:** Explicitly passing the embedding model improves modularity, allowing model replacement or tuning without refactoring function internals.

3. **Installed `pinecone` instead of deprecated `pinecone-client`**

   * **Reasoning:** The older package is deprecated and incompatible with new API structures; this ensures long-term forward compatibility.

---

### **Improvements**

1. **Integrated SentenceTransformer embedding model (`all-MiniLM-L6-v2`)**

   * **Reasoning:** Offers fast, lightweight, open-source embeddings suitable for semantic search. Removes dependency on paid embedding APIs.

2. **Standardized environment configuration from `config.py`**

   * **Reasoning:** Centralizing configurations reduces redundancy and risk of mismatched parameters. Simplifies environment setup and scaling.

---

### **Thought Process**

This refactor focused on **modernizing the data ingestion pipeline**. The objective was to ensure:

* Compatibility with the new Pinecone SDK.
* Free and high-quality embeddings.
* Consistent and centralized configuration for scalability.

By making the embedding model explicit and API-compatible, the script is now stable for large dataset uploads and easier to maintain.

---

## visualize_graph.py

### **Improvement**

* **Upgraded pyvis from 0.3.1 → 0.3.2** to fix `net.show()` bug (`notebook=False` incompatibility).

  * **Reasoning:** Prevents runtime errors during visualization rendering and allows smooth generation of HTML-based graph views.

### **Thought Process**

This change ensures the visualization step runs without manual workarounds or notebook constraints, supporting standalone HTML rendering for Neo4j relationship graphs.

---

## load_to_neo4j.py

### **Improvement**

1. **Configured data to load into `vietnam-travel` database created inside instance of Neo4j instead of default**

   * **Reasoning:** Keeps project data isolated, avoiding conflicts with other datasets or default system databases. It also helps maintain a clean, domain-specific data environment.

### **Thought Process**

This modification reflects a focus on **data organization and maintainability**. Dedicated databases allow targeted queries and cleaner scaling when multiple domains or datasets are introduced later.



