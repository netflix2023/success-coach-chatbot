import os
import chromadb
from chromadb.utils import embedding_functions

# -------------------------------------------------------------------
# 1. Configuration & Data Definition
# -------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "dallas_college_success_coach"

# Sample student success coach database chunks
KNOWLEDGE_BASE = [
    {
        "id": "cosc_1436_reqs",
        "title": "Dallas College Course Catalog: COSC 1436",
        "url": "https://catalog.dallascollege.edu/preview_course_nopop.php?catoid=33&coid=102347",
        "content": "COSC 1436 Programming Fundamentals I (4 credits). This course introduces the fundamental concepts of structured programming, and provides a comprehensive introduction to programming in computer science. Topics include data types, control structures, functions, arrays, and the mechanics of running, testing, and debugging. Prerequisites: None. Corequisite: None. Required: Complete TSI eligibility in mathematics and reading/writing."
    },
    {
        "id": "richland_coaching_office",
        "title": "Richland Campus Directory: Sabine Hall S-203",
        "url": "https://www.dallascollege.edu/about/locations/richland/pages/campus-map.aspx",
        "content": "The Success Coaching Office at the Richland Campus is located on the second floor of Sabine Hall (S Building), Room S-203. Standard operational hours are Monday through Thursday from 8:00 AM to 7:00 PM, and Friday from 8:00 AM to 5:00 PM. Contact email: richlandcoaching@dallascollege.edu."
    },
    {
        "id": "utd_transfer_guide",
        "title": "Dallas College Articulation Agreements: UT Dallas Guide",
        "url": "https://www.dallascollege.edu/admissions/transfer/pages/utdallas.aspx",
        "content": "Under the formal articulation agreement between Dallas College and the University of Texas at Dallas (UTD), students completing an Associate of Science in Computer Science can transfer up to 60 credits directly towards a Bachelor of Science in Computer Science. A minimum grade of 'C' is required for all transferable courses. Key contact: transfer@dallascollege.edu."
    },
    {
        "id": "financial_aid_deadlines",
        "title": "Dallas College Financial Aid Portal",
        "url": "https://www.dallascollege.edu/admissions/financial-aid/pages/default.aspx",
        "content": "Priority deadlines for Dallas College financial aid applications (FAFSA/TASFA) are January 15 for the Fall semester, and September 1 for the Spring semester. Late applications are accepted but funding is awarded on a first-come, first-served basis. Office location: Sabine Hall Room S-102."
    }
]

def setup_chromadb():
    print(f"Initializing persistent ChromaDB client at: {DB_PATH}")
    
    # Initialize Persistent ChromaDB Client
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Use Chroma's default Sentence Transformer embedding function (all-MiniLM-L6-v2)
    # This downloads the lightweight model locally on the first run and operates 100% offline.
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    print(f"Getting or creating collection: '{COLLECTION_NAME}'")
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=default_ef
    )
    
    # Prepare documents, metadata, and unique IDs
    documents = []
    metadatas = []
    ids = []
    
    for item in KNOWLEDGE_BASE:
        documents.append(item["content"])
        metadatas.append({
            "title": item["title"],
            "url": item["url"]
        })
        ids.append(item["id"])
        
    print(f"Upserting {len(documents)} document chunks into collection...")
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Successfully populated ChromaDB!")
    
    # Test Query
    test_query = "What are the requirements for COSC 1436?"
    print(f"\n🔍 Testing similarity search query: '{test_query}'")
    
    results = collection.query(
        query_texts=[test_query],
        n_results=2
    )
    
    print("\nSearch Results:")
    for idx, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0], 
        results['metadatas'][0], 
        results['distances'][0]
    )):
        print(f"\n[{idx + 1}] {metadata['title']}")
        print(f"    Distance Score: {distance:.4f}")
        print(f"    Source Link: {metadata['url']}")
        print(f"    Snippet: {doc}")

if __name__ == "__main__":
    setup_chromadb()
