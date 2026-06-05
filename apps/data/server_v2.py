"""
server_v2.py — Dallas College Success Coach Chatbot Backend (v2)

Pluggable retriever pipeline:
  Query → Retriever → Context Assembly → LLM (Gemini) → Response

Retriever modes (auto-detected on startup):
  - MockRetriever:   ~20 hardcoded entries covering courses, programs, transfers, etc.
  - JSONRetriever:   loads scraped/courses.json + scraped/programs.json, TF-IDF search
  - ChromaRetriever: (stub) future ChromaDB vector store

API contract (unchanged from v1):
  POST /api/chat  {"query": "..."}  →  {"answer": "...", "sources": [...]}
  GET  /api/health                  →  {"status": "ok", "mode": "...", "documents": N}

Stdlib-only — no pip installs required.
"""

import http.server
import socketserver
import json
import urllib.request
import urllib.error
import os
import re
import math
from abc import ABC, abstractmethod

# ============================================================================
# 0. Environment / Config
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env():
    """Load .env from parent directory (apps/.env)."""
    env = {}
    for candidate in [os.path.join(SCRIPT_DIR, "..", ".env"),
                      os.path.join(SCRIPT_DIR, ".env")]:
        if os.path.exists(candidate):
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if line and "=" in line and not line.startswith("#"):
                        key, val = line.split("=", 1)
                        env[key.strip()] = val.strip()
            break
    return env

ENV = load_env()
GEMINI_API_KEY = ENV.get("GEMINI_API_KEY", "")
PORT = int(ENV.get("PORT", 8080))

# ============================================================================
# 1. Mock Knowledge Base (~20 entries)
# ============================================================================

MOCK_KNOWLEDGE_BASE = [
    # --- 5 Popular Courses ---
    {
        "id": "cosc_1436",
        "title": "Dallas College Course Catalog: COSC 1436 — Programming Fundamentals I",
        "url": "https://catalog.dallascollege.edu/preview_course_nopop.php?catoid=33&coid=102347",
        "content": (
            "COSC 1436 Programming Fundamentals I (4 credits). Introduces fundamental concepts "
            "of structured programming and provides a comprehensive introduction to programming "
            "for computer science. Topics include data types, control structures, functions, "
            "arrays, and the mechanics of running, testing, and debugging. "
            "Prerequisites: None. Required: TSI eligibility in mathematics and reading/writing."
        ),
    },
    {
        "id": "cosc_1437",
        "title": "Dallas College Course Catalog: COSC 1437 — Programming Fundamentals II",
        "url": "https://catalog.dallascollege.edu/preview_course_nopop.php?catoid=33&coid=102348",
        "content": (
            "COSC 1437 Programming Fundamentals II (4 credits). Continuation of COSC 1436. "
            "Covers object-oriented programming including classes, inheritance, polymorphism, "
            "exception handling, recursion, and file I/O. Students build larger programs and "
            "practice software design principles. Prerequisite: COSC 1436 with grade C or better."
        ),
    },
    {
        "id": "itsy_1300",
        "title": "Dallas College Course Catalog: ITSY 1300 — Fundamentals of Information Security",
        "url": "https://catalog.dallascollege.edu/preview_course_nopop.php?catoid=33&coid=103210",
        "content": (
            "ITSY 1300 Fundamentals of Information Security (3 credits). An introduction to "
            "information security including vocabulary, security layers, threats, attacks, and "
            "countermeasures. Covers access control, cryptography, network security, and "
            "security policy development. This is the gateway course for the Cybersecurity AAS."
        ),
    },
    {
        "id": "math_1314",
        "title": "Dallas College Course Catalog: MATH 1314 — College Algebra",
        "url": "https://catalog.dallascollege.edu/preview_course_nopop.php?catoid=33&coid=104001",
        "content": (
            "MATH 1314 College Algebra (3 credits). In-depth study and applications of "
            "polynomial, rational, radical, exponential, and logarithmic functions, systems of "
            "equations, and inequalities. Additional topics may include sequences, series, and "
            "probability. Prerequisite: TSI complete in math or MATH 0314 with grade C or better."
        ),
    },
    {
        "id": "engl_1301",
        "title": "Dallas College Course Catalog: ENGL 1301 — Composition I",
        "url": "https://catalog.dallascollege.edu/preview_course_nopop.php?catoid=33&coid=104100",
        "content": (
            "ENGL 1301 Composition I (3 credits). Intensive study of and practice in writing "
            "processes, from invention and researching to drafting, revising, and editing, both "
            "individually and collaboratively. Emphasis on effective rhetorical choices including "
            "audience, purpose, arrangement, and style. Prerequisite: TSI complete in writing."
        ),
    },

    # --- 3 Degree Programs ---
    {
        "id": "as_cs",
        "title": "Dallas College Program: Associate of Science in Computer Science",
        "url": "https://catalog.dallascollege.edu/preview_program.php?catoid=33&poid=12345",
        "content": (
            "The Associate of Science (AS) in Computer Science is a 60-credit-hour transfer "
            "degree designed for students planning to transfer to a four-year university. "
            "Core courses include COSC 1436, COSC 1437, COSC 2436 (Data Structures), "
            "MATH 2413 (Calculus I), MATH 2414 (Calculus II), and PHYS 2425 (Physics I). "
            "Students must maintain a 2.0 GPA and complete all Texas Core Curriculum requirements."
        ),
    },
    {
        "id": "aas_cyber",
        "title": "Dallas College Program: AAS in Cybersecurity",
        "url": "https://catalog.dallascollege.edu/preview_program.php?catoid=33&poid=12350",
        "content": (
            "The Associate of Applied Science (AAS) in Cybersecurity is a 60-credit workforce "
            "degree preparing students for entry-level cybersecurity roles. Courses include "
            "ITSY 1300, ITSY 2300 (Operating System Security), ITSY 2301 (Firewalls & "
            "Network Security), and ITSY 2343 (Computer Forensics). Graduates are prepared "
            "for CompTIA Security+, CySA+, and other industry certifications."
        ),
    },
    {
        "id": "aa_general",
        "title": "Dallas College Program: Associate of Arts in General Studies",
        "url": "https://catalog.dallascollege.edu/preview_program.php?catoid=33&poid=12300",
        "content": (
            "The Associate of Arts (AA) in General Studies is a flexible 60-credit transfer "
            "degree allowing students to explore multiple disciplines. Students complete the "
            "42-hour Texas Core Curriculum plus 18 hours of electives. Popular elective areas "
            "include psychology, sociology, history, and communications. This degree transfers "
            "to most Texas public universities under the Texas Common Course Numbering System."
        ),
    },

    # --- 3 Transfer Guides ---
    {
        "id": "transfer_utd",
        "title": "Transfer Guide: Dallas College → UT Dallas",
        "url": "https://www.dallascollege.edu/admissions/transfer/pages/utdallas.aspx",
        "content": (
            "Under the articulation agreement between Dallas College and the University of "
            "Texas at Dallas (UTD), students completing an AS in Computer Science can transfer "
            "up to 60 credits toward a BS in Computer Science. A minimum grade of 'C' is "
            "required for all transferable courses. UTD also guarantees admission for Dallas "
            "College graduates with a 3.0+ GPA through the Comet Connection program. "
            "Contact: transfer@dallascollege.edu."
        ),
    },
    {
        "id": "transfer_uta",
        "title": "Transfer Guide: Dallas College → UT Arlington",
        "url": "https://www.dallascollege.edu/admissions/transfer/pages/utarlington.aspx",
        "content": (
            "The Dallas College to UT Arlington (UTA) transfer pathway allows AS and AA "
            "graduates to transfer seamlessly. UTA accepts all Texas Core Curriculum hours. "
            "The Maverick Transfer Guarantee ensures admission for students with an associate "
            "degree and 2.5+ GPA. Engineering and nursing programs have additional prerequisites. "
            "UTA campus visits can be scheduled through the Dallas College Transfer Center."
        ),
    },
    {
        "id": "transfer_unt",
        "title": "Transfer Guide: Dallas College → University of North Texas",
        "url": "https://www.dallascollege.edu/admissions/transfer/pages/unt.aspx",
        "content": (
            "Dallas College has a comprehensive transfer agreement with the University of "
            "North Texas (UNT). The Eagle Transfer Guarantee ensures admission for students "
            "completing an associate degree with a 2.25+ GPA. UNT accepts all completed Texas "
            "Core Curriculum courses. Students interested in computer science, business, or "
            "education should meet with a transfer advisor for program-specific mapping."
        ),
    },

    # --- 3 Financial Aid ---
    {
        "id": "fafsa_deadlines",
        "title": "Dallas College Financial Aid: FAFSA/TASFA Deadlines",
        "url": "https://www.dallascollege.edu/admissions/financial-aid/pages/default.aspx",
        "content": (
            "Priority deadlines for Dallas College financial aid applications: FAFSA/TASFA "
            "due January 15 for Fall semester, September 1 for Spring semester. Late "
            "applications are accepted but funding is first-come, first-served. The Dallas "
            "College school code for FAFSA is 014062. Financial aid office: Sabine Hall S-102. "
            "Email: financialaid@dallascollege.edu."
        ),
    },
    {
        "id": "scholarships",
        "title": "Dallas College Financial Aid: Scholarships",
        "url": "https://www.dallascollege.edu/admissions/financial-aid/pages/scholarships.aspx",
        "content": (
            "Dallas College offers institutional scholarships including the Rising Star "
            "Scholarship (full tuition for eligible DISD graduates), Chancellor's Excellence "
            "Award ($2,000/semester for 3.5+ GPA), and the STEM Pathway Scholarship for "
            "students in science, technology, engineering, or math programs. Applications open "
            "March 1 each year. Visit the scholarship portal at dallascollege.edu/scholarships."
        ),
    },
    {
        "id": "payment_plans",
        "title": "Dallas College Financial Aid: Payment Plans",
        "url": "https://www.dallascollege.edu/admissions/financial-aid/pages/payment-plans.aspx",
        "content": (
            "Dallas College offers installment payment plans through Nelnet. Students can split "
            "tuition into 3-4 monthly payments with a $35 enrollment fee. Payment plans must be "
            "set up before the semester payment deadline. Emergency short-term loans are also "
            "available for students facing unexpected financial hardship. Contact the Business "
            "Office or visit eConnect for details."
        ),
    },

    # --- 3 Campus / Advising ---
    {
        "id": "richland_coaching",
        "title": "Richland Campus: Success Coaching Office",
        "url": "https://www.dallascollege.edu/about/locations/richland/pages/campus-map.aspx",
        "content": (
            "The Success Coaching Office at Richland Campus is in Sabine Hall (S Building), "
            "Room S-203. Hours: Monday–Thursday 8:00 AM–7:00 PM, Friday 8:00 AM–5:00 PM. "
            "Success Coaches help with academic planning, degree audits, course registration, "
            "and career exploration. Walk-ins welcome; appointments available via Navigate. "
            "Email: richlandcoaching@dallascollege.edu."
        ),
    },
    {
        "id": "advising_general",
        "title": "Dallas College: Academic Advising Services",
        "url": "https://www.dallascollege.edu/admissions/advising/pages/default.aspx",
        "content": (
            "Dallas College provides academic advising at all seven campuses. Advisors help "
            "students select courses, plan degree pathways, and prepare for transfer. New "
            "students must complete a mandatory advising session before their first registration. "
            "Returning students are encouraged to meet with an advisor each semester. Schedule "
            "appointments through Navigate or call your campus advising center."
        ),
    },
    {
        "id": "campus_locations",
        "title": "Dallas College: Campus Locations & Hours",
        "url": "https://www.dallascollege.edu/about/locations/pages/default.aspx",
        "content": (
            "Dallas College has seven campuses: Brookhaven, Cedar Valley, Eastfield, El Centro, "
            "Mountain View, North Lake, and Richland. All campuses are open Monday–Thursday "
            "7:00 AM–9:00 PM, Friday 7:00 AM–5:00 PM, Saturday 8:00 AM–2:00 PM (select "
            "services). Each campus has a library, tutoring center, testing center, and "
            "student success center. Visit dallascollege.edu/locations for maps and directions."
        ),
    },

    # --- 3 Student Services ---
    {
        "id": "tutoring",
        "title": "Dallas College: Tutoring & Academic Support",
        "url": "https://www.dallascollege.edu/academics/resources/tutoring/pages/default.aspx",
        "content": (
            "Free tutoring is available at all Dallas College campuses through the Academic "
            "Success Centers. Subjects include math, science, writing, and computer science. "
            "Online tutoring is available 24/7 through Brainfuse. Peer tutoring, group study "
            "sessions, and supplemental instruction (SI) are also offered for high-enrollment "
            "courses. No appointment needed for drop-in tutoring."
        ),
    },
    {
        "id": "registration",
        "title": "Dallas College: Registration & Enrollment Steps",
        "url": "https://www.dallascollege.edu/admissions/registration/pages/default.aspx",
        "content": (
            "To register for classes at Dallas College: (1) Apply online at apply.dallascollege.edu, "
            "(2) Submit TSI scores or exemption documentation, (3) Complete mandatory new-student "
            "advising, (4) Register for classes through eConnect, (5) Pay tuition by the payment "
            "deadline. In-district tuition is approximately $59/credit hour. Late registration "
            "incurs a $50 fee."
        ),
    },
    {
        "id": "career_services",
        "title": "Dallas College: Career Services & Job Placement",
        "url": "https://www.dallascollege.edu/academics/resources/career-services/pages/default.aspx",
        "content": (
            "Dallas College Career Services offers resume workshops, mock interviews, career "
            "assessments, and job fairs each semester. Handshake is the official job board for "
            "internship and employment listings. Career counselors can help students explore "
            "career options aligned with their degree pathway. Services are free for all current "
            "students and alumni within one year of graduation."
        ),
    },
]

# ============================================================================
# 2. TF-IDF Engine (stdlib-only)
# ============================================================================

# Stopwords to ignore during TF-IDF computation (common English words)
_STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did will would "
    "shall should may might can could of in to for on with at by from as into "
    "through during before after above below between out off over under again "
    "further then once here there when where why how all each every both few "
    "more most other some such no nor not only own same so than too very and "
    "but if or because until while about against".split()
)


def tokenize(text):
    """Lowercase tokenize, remove stopwords, return list of words."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS]


def compute_tf(tokens):
    """Term frequency: count of each token / total tokens."""
    tf = {}
    total = len(tokens) if tokens else 1
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    return {t: c / total for t, c in tf.items()}


def compute_idf(doc_token_lists):
    """Inverse document frequency across a corpus. Returns {term: idf}."""
    n = len(doc_token_lists)
    df = {}  # document frequency
    for tokens in doc_token_lists:
        seen = set(tokens)
        for t in seen:
            df[t] = df.get(t, 0) + 1
    # IDF with smoothing: log((N + 1) / (df + 1)) + 1
    return {t: math.log((n + 1) / (count + 1)) + 1 for t, count in df.items()}


def tfidf_vector(tf, idf):
    """Build a TF-IDF vector dict."""
    return {t: tf_val * idf.get(t, 1.0) for t, tf_val in tf.items()}


def cosine_similarity(vec_a, vec_b):
    """Cosine similarity between two sparse vectors (dicts)."""
    # Dot product
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in set(vec_a) | set(vec_b))
    # Magnitudes
    mag_a = math.sqrt(sum(v * v for v in vec_a.values())) if vec_a else 0
    mag_b = math.sqrt(sum(v * v for v in vec_b.values())) if vec_b else 0
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


# ============================================================================
# 3. Retriever Interface & Implementations
# ============================================================================

class BaseRetriever(ABC):
    """Abstract retriever — all retrievers implement this interface."""

    @abstractmethod
    def search(self, query, top_k=3):
        """Return list of dicts with keys: id, title, url, content, score."""
        ...

    @abstractmethod
    def doc_count(self):
        """Number of documents in the index."""
        ...

    @property
    @abstractmethod
    def mode_name(self):
        """String identifier for /api/health."""
        ...


class MockRetriever(BaseRetriever):
    """Uses the hardcoded MOCK_KNOWLEDGE_BASE with TF-IDF search."""

    def __init__(self):
        self._docs = MOCK_KNOWLEDGE_BASE
        self._build_index()

    def _build_index(self):
        """Pre-compute IDF and per-doc TF-IDF vectors."""
        self._token_lists = []
        self._tf_vectors = []
        for doc in self._docs:
            tokens = tokenize(doc["title"] + " " + doc["content"])
            self._token_lists.append(tokens)
            self._tf_vectors.append(compute_tf(tokens))
        self._idf = compute_idf(self._token_lists)
        self._tfidf_vectors = [tfidf_vector(tf, self._idf) for tf in self._tf_vectors]

    def search(self, query, top_k=3):
        query_tokens = tokenize(query)
        query_tf = compute_tf(query_tokens)
        query_vec = tfidf_vector(query_tf, self._idf)

        scored = []
        for i, doc_vec in enumerate(self._tfidf_vectors):
            score = cosine_similarity(query_vec, doc_vec)
            if score > 0.02:
                scored.append((score, self._docs[i]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {**doc, "score": round(score, 4)}
            for score, doc in scored[:top_k]
        ]

    def doc_count(self):
        return len(self._docs)

    @property
    def mode_name(self):
        return "mock"


class JSONRetriever(BaseRetriever):
    """Loads scraped JSON files and performs TF-IDF search over them."""

    def __init__(self, scraped_dir):
        self._docs = []
        self._load_files(scraped_dir)
        self._build_index()

    def _load_files(self, scraped_dir):
        """Load courses.json and programs.json into a unified doc list."""
        for filename in ["courses.json", "programs.json", "general_pages.json"]:
            filepath = os.path.join(scraped_dir, filename)
            if not os.path.exists(filepath):
                continue
            try:
                with open(filepath) as f:
                    items = json.load(f)
                if not isinstance(items, list):
                    continue
                for item in items:
                    doc = self._normalize(item, filename)
                    if doc:
                        self._docs.append(doc)
            except (json.JSONDecodeError, IOError) as e:
                print(f"  Warning: could not load {filepath}: {e}")

        print(f"  JSONRetriever loaded {len(self._docs)} documents from {scraped_dir}")

    def _normalize(self, item, source_file):
        """Convert scraped JSON item into a standard doc dict."""
        # courses.json format
        if "prefix" in item and "number" in item:
            doc_id = f"{item['prefix']}_{item['number']}".lower()
            title = item.get("title", f"{item['prefix']} {item['number']}")
            content = item.get("description", "")
            prereqs = item.get("prerequisites", "")
            if prereqs:
                content += f" Prerequisites: {prereqs}"
            url = item.get("url", "")
            return {"id": doc_id, "title": title, "url": url, "content": content}

        # programs.json format
        if "program_name" in item or "title" in item:
            title = item.get("program_name", item.get("title", ""))
            content = item.get("description", item.get("content", ""))
            url = item.get("url", "")
            doc_id = re.sub(r"[^a-z0-9]+", "_", title.lower())[:60]
            return {"id": doc_id, "title": title, "url": url, "content": content}

        # general_pages.json — flexible fallback
        if "title" in item or "content" in item or "text" in item:
            title = item.get("title", "Untitled")
            content = item.get("content", item.get("text", item.get("description", "")))
            url = item.get("url", "")
            doc_id = re.sub(r"[^a-z0-9]+", "_", title.lower())[:60]
            return {"id": doc_id, "title": title, "url": url, "content": content}

        return None

    def _build_index(self):
        """Pre-compute TF-IDF vectors."""
        self._token_lists = []
        self._tf_vectors = []
        for doc in self._docs:
            text = (doc.get("title", "") + " " + doc.get("content", "")).strip()
            tokens = tokenize(text)
            self._token_lists.append(tokens)
            self._tf_vectors.append(compute_tf(tokens))
        self._idf = compute_idf(self._token_lists)
        self._tfidf_vectors = [tfidf_vector(tf, self._idf) for tf in self._tf_vectors]

    def search(self, query, top_k=3):
        query_tokens = tokenize(query)
        query_tf = compute_tf(query_tokens)
        query_vec = tfidf_vector(query_tf, self._idf)

        scored = []
        for i, doc_vec in enumerate(self._tfidf_vectors):
            score = cosine_similarity(query_vec, doc_vec)
            if score > 0.01:
                scored.append((score, self._docs[i]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {**doc, "score": round(score, 4)}
            for score, doc in scored[:top_k]
        ]

    def doc_count(self):
        return len(self._docs)

    @property
    def mode_name(self):
        return "json"


class ChromaRetriever(BaseRetriever):
    """Stub — will connect to ChromaDB vector store in a future iteration."""

    def __init__(self, collection_name="dallas_college", host="localhost", port=8000):
        self._collection_name = collection_name
        self._host = host
        self._port = port
        # TODO: Initialize chromadb.HttpClient here
        print(f"  ChromaRetriever stub initialized (collection={collection_name})")

    def search(self, query, top_k=3):
        # TODO: self._collection.query(query_texts=[query], n_results=top_k)
        return []

    def doc_count(self):
        # TODO: return self._collection.count()
        return 0

    @property
    def mode_name(self):
        return "chromadb"


# ============================================================================
# 4. Auto-detect retriever on startup
# ============================================================================

def create_retriever():
    """Pick the best available retriever based on what data exists."""
    scraped_dir = os.path.join(SCRIPT_DIR, "scraped")
    courses_path = os.path.join(scraped_dir, "courses.json")

    # Check for scraped JSON data first
    if os.path.exists(courses_path):
        try:
            with open(courses_path) as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                print(f"[STARTUP] Found scraped data at {scraped_dir}")
                retriever = JSONRetriever(scraped_dir)
                if retriever.doc_count() > 0:
                    return retriever
                print("  Warning: JSONRetriever loaded 0 documents, falling back to mock.")
        except Exception as e:
            print(f"  Warning: Failed to load courses.json: {e}")

    # Default: mock data
    print("[STARTUP] Using MockRetriever with ~20 hardcoded entries")
    return MockRetriever()


# ============================================================================
# 5. Context Assembly & LLM Call
# ============================================================================

SYSTEM_PERSONA = (
    "You are Ali, the official Dallas College Success Coach AI assistant. "
    "You help students with course information, degree planning, transfer guidance, "
    "financial aid, and campus services. "
    "Answer using ONLY the provided Context sources. "
    "Cite facts with the source marker (e.g., [1], [2]) at the end of relevant sentences. "
    "Keep answers concise (3-5 sentences). Be warm and encouraging."
)

FALLBACK_SOURCES = [
    {"num": 1, "name": "Dallas College Success Coach Directory",
     "url": "https://www.dallascollege.edu/admissions/advising/pages/coaches.aspx"},
    {"num": 2, "name": "Dallas College Contact Directory",
     "url": "https://www.dallascollege.edu/about/pages/contact.aspx"},
]


def build_prompt(query, matched_docs):
    """Assemble the LLM prompt from query + retrieved context."""
    if matched_docs:
        context_parts = []
        for i, doc in enumerate(matched_docs):
            context_parts.append(
                f"Source [{i+1}]: {doc['title']}\n{doc['content']}"
            )
        context_str = "\n\n".join(context_parts)
        return (
            f"{SYSTEM_PERSONA}\n\n"
            f"Context:\n{context_str}\n\n"
            f"Student Question: {query}"
        )
    else:
        return (
            f"{SYSTEM_PERSONA}\n\n"
            f"Student asked: '{query}'. No matching documents were found in the knowledge base. "
            "Respond politely that you couldn't find specific information, and suggest they "
            "contact their Success Coach [1] or check the Dallas College directory [2]."
        )


def call_gemini(prompt, timeout=10):
    """Call Gemini API. Returns answer text or None on failure."""
    if not GEMINI_API_KEY or "Fake" in GEMINI_API_KEY:
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 512,
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"  Gemini API error: {e}")
        return None


def offline_fallback(query, matched_docs):
    """Generate a reasonable offline answer when Gemini is unavailable."""
    if matched_docs:
        doc = matched_docs[0]
        # Trim content to a readable snippet
        snippet = doc["content"][:200].rsplit(" ", 1)[0]
        return (
            f"Based on **{doc['title']}** [1]: {snippet}... "
            "Please check the source link for full details."
        )
    return (
        "I'm sorry, I couldn't find information matching your question in our knowledge base. "
        "I recommend reaching out to your Success Coach [1] or checking the Dallas College "
        "directory [2] for assistance."
    )


# ============================================================================
# 6. HTTP Server
# ============================================================================

# Global retriever — initialized at startup
RETRIEVER = None


class ChatHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with /api/chat and /api/health endpoints."""

    def _send_cors_headers(self):
        """Add CORS headers so the Next.js frontend can call us."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status_code, obj):
        """Helper: send a JSON response with CORS."""
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    # -- CORS preflight --
    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    # -- Health check --
    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(200, {
                "status": "ok",
                "mode": RETRIEVER.mode_name,
                "documents": RETRIEVER.doc_count(),
            })
        else:
            # Serve static files (e.g., prototype.html)
            super().do_GET()

    # -- Chat endpoint --
    def do_POST(self):
        if self.path != "/api/chat":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length)
            data = json.loads(raw.decode("utf-8"))
            query = data.get("query", "").strip()

            if not query:
                self._send_json(400, {"error": "Missing 'query' field"})
                return

            # --- Pipeline: Retrieve → Assemble → Generate ---

            # Step 1: Retrieve
            matched_docs = RETRIEVER.search(query, top_k=3)

            # Step 2: Build sources list
            if matched_docs:
                sources = [
                    {"num": i + 1, "name": doc["title"], "url": doc["url"]}
                    for i, doc in enumerate(matched_docs)
                ]
            else:
                sources = FALLBACK_SOURCES

            # Step 3: Assemble prompt
            prompt = build_prompt(query, matched_docs)

            # Step 4: Call LLM (with offline fallback)
            answer = call_gemini(prompt)
            if answer is None:
                answer = offline_fallback(query, matched_docs)

            # Step 5: Respond
            self._send_json(200, {"answer": answer, "sources": sources})

        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
        except Exception as e:
            print(f"  Error handling /api/chat: {e}")
            self._send_json(500, {"error": str(e)})

    # Suppress default request logging noise
    def log_message(self, format, *args):
        print(f"  [{self.command}] {self.path} — {args[0] if args else ''}")


# ============================================================================
# 7. Main
# ============================================================================

def main():
    global RETRIEVER

    print("=" * 60)
    print("  Dallas College Success Coach — server_v2.py")
    print("=" * 60)

    # Auto-detect retriever
    RETRIEVER = create_retriever()
    print(f"[STARTUP] Mode: {RETRIEVER.mode_name} | Documents: {RETRIEVER.doc_count()}")
    print(f"[STARTUP] Gemini API key: {'configured' if GEMINI_API_KEY and 'Fake' not in GEMINI_API_KEY else 'NOT SET (offline mode)'}")

    # Start server
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), ChatHandler) as httpd:
        print(f"[STARTUP] Listening on http://127.0.0.1:{PORT}/")
        print(f"[STARTUP] Endpoints:")
        print(f"           POST /api/chat    — {{\"query\": \"...\"}}")
        print(f"           GET  /api/health  — status check")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
