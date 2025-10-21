# 🧠 Hybrid AI Travel Assistant
## 🚀 Overview

This project builds a **travel assistant** that can understand natural-language questions and respond using data retrieved from both **Pinecone**  and **Neo4j**.
It has been fully refactored to remove deprecated APIs and replace paid dependencies with open, modern, and cost-free equivalents.

##  Project Structure

```
Hybrid-AI-chat/
│
├── hybrid_chat_new.py                    # Main conversational logic (hybrid retrieval)
├── pinecone_upload_sentenceTransform.py  # Uploads embeddings to Pinecone
├── load_to_neo4j.py                      # Loads dataset into Neo4j
├── visualize_graph.py                    # Generates HTML graph visualization
├── vietnam_travel_dataset.json           # Travel knowledge base
├── config.py                             # Environment keys (ignored in .gitignore)
├── requirements.txt                      # Dependencies
└── improvements.md                       # Summary of bug fixes and enhancements
```

---

##  Setup Instructions

1. **Set up environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Add your keys in `config.py`**

3. **Load data into Neo4j**

   ```bash
   python load_to_neo4j.py
   ```

4. **Visualize the graph (optional)**

   ```bash
   python visualize_graph.py
   ```

   ➡ Generates `neo4j_viz.html`

5. **Upload embeddings to Pinecone**

   ```bash
   python pinecone_upload_sentenceTransform.py
   ```

6. **Run hybrid chat**

   ```bash
   python hybrid_chat.py
   ```

   Example query:

   ```
   Enter your travel question: create a romantic 4 day itinerary for Vietnam
   ```
** NOTE : Make sure neo4j is installed on local device and running in the background before running hybrid_chat_new.py or any neo4j related files.**
---

##  Key Improvements

| Area              | Improvement                                      | Impact                                          |
| ----------------- | ------------------------------------------------ | ----------------------------------------------- |
| **Pinecone**      | Migrated to v2 SDK, updated index handling       | Fixes deprecated methods, ensures compatibility |
| **Embeddings**    | Switched to `all-MiniLM-L6-v2`                   | Free, fast, and accurate semantic embeddings    |
| **Model**         | Replaced GPT-4o-mini → `LLaMA 3.3-70B Versatile` | Enables open-source, high-performance reasoning |
| **Integration**   | Added `search_summary()`                         | Summarizes hybrid retrieval results             |
| **Prompting**     | Enhanced chain-of-thought and context clarity    | Improves reasoning and itinerary coherence      |
| **Visualization** | Upgraded PyVis to 0.3.2                          | Fixed `notebook=False` bug for HTML export      |
| **Neo4j**         | Targeted `vietnam-travel` database               | Keeps data isolated and domain-specific         |

---

##  Deliverables

| Task       | Deliverable                                     |
| ---------- | ----------------------------------------------- |
| **Task 1** | Screenshot of successful Pinecone uploads       |

| **Task 2** | Working CLI chat session using hybrid retrieval |

| **Task 3** | Documented improvements (`improvements.md`)     |


