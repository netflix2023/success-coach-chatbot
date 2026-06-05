# MVP Requirements: Success Coach Chatbot
> **Project Goal**: Build an intelligent success coach chatbot for Dallas College in collaboration with the AI Club to assist student aids, advisors, and students.
> **Scope**: Lightweight, embeddable floating web widget providing instant RAG-based answers to campus resources, degree requirements, event schedules, and advisor directories.

---

## 1. Core Objectives
1. **Accelerate Assistance**: Empower student aids and advisors with rapid, accurate search capabilities across scattered academic resources.
2. **24/7 Availability**: Provide students with immediate answers to degree requirements, campus transfers, financial aid options, and events.
3. **Embeddable & Non-Intrusive**: Ensure the widget can float cleanly in the corner of any Dallas College webpage using a simple JS snippet.

---

## 2. Feature Priority Matrix

To ensure the club delivers a high-impact, achievable system in **10–12 weeks**, we group functions into **MVP Core (Phase 1)** and **Future Expansions (Phase 2)**.

| Feature Area | Functions Included | Required Data Source | MVP Status | Priority |
| :--- | :--- | :--- | :--- | :--- |
| **Degree & Program Planning** | Course requirements, program of study, academic catalogs. | Scraping & PDF catalogs | **MVP Core** | Critical |
| **Course Information** | Catalog course descriptions, prerequisites, corequisites. | Dallas College Catalog | **MVP Core** | High |
| **Advisor Directory & Contacts** | Advisor contact info, office locations, transfer contacts. | Dallas College Directory | **MVP Core** | High |
| **Financial Aid & Scholarships** | Scholarship applications, grant eligibility, FAFSA info. | Dallas College FinAid Pages | **MVP Core** | Medium |
| **Event Finder** | Club schedules, academic workshops, calendar events. | Scraping / Club feeds | **MVP Core** | Medium |
| **Navigation & Quick Links** | Resource links, maps, Lost & Found guidelines. | Web links / Static PDFs | **MVP Core** | Low |
| **Syllabuses & Vitae** | Professor profiles, official syllabuses, vitae database. | Dallas College e-Connect | *Phase 2* | Nice-to-Have |
| **Advisor Scheduling** | Direct booking integration with scheduling systems. | Live API Integration | *Phase 2* | Out of Scope |
| **Student Record Lookup** | Viewing personal course history or academic status. | Mock Student DB API | *Phase 2* | Out of Scope |
| **Feedback & Complaints** | Submitting user feedback, complaints, or reports. | Database backend POST | *Phase 2* | Low |

---

## 3. MVP Core Capabilities

### 🏛️ RAG (Retrieval-Augmented Generation) & Knowledge Base
The AI engineering and data teams will implement a RAG pipeline that scrapes, indexes, and searches public Dallas College data.
* **Academic Catalog Search**: Ask "What are the prerequisites for COSC 1436?" or "How many credits are needed for an Associate of Science?"
* **Advisor Information**: Retrieve "Who is the transfer contact for UT Dallas?" or "Where is the success coaching office at Richland campus?"
* **General Campus Info**: Address FAQs on lost & found policies, financial aid deadlines, and active student clubs.

### 💬 The Widget Interface (The Front Door)
* **Floating Widget Trigger**: A subtle, beautifully designed "Chat with Us" circle in the bottom right corner of the host site.
* **Isolated Floating Container**: The chat window renders in an overlay container (or an `<iframe>` container) to prevent CSS leaks from the host page.
* **Streaming Response Output**: Real-time response generation (tokens print word-by-word) utilizing the Vercel AI SDK to prevent frustrating wait-states.

### 🛡️ Guardrails & Safety
* **Advisor Escalation**: When the LLM is unsure or the request involves complex, high-stakes academic planning, it prints advisor contact information with an explicit message: *"Please consult with an official Dallas College Success Coach for final degree validation."*
* **Hallucination Protection**: Prompt guidelines constrain the LLM to only answer based on retrieved context. If the answer is not in the context, it gracefully says: *"I'm sorry, I couldn't find that specific details in the Dallas College catalog. Let me connect you with an advisor or search the site."*

---

## 4. Success Criteria

> [!IMPORTANT]
> The MVP must fulfill three main performance bars before club deployment:
> 1. **Response Speed (Latency)**: Time-to-first-token must be under **1.2 seconds**. We will achieve this through structured stream responses and vector DB indexing.
> 2. **Correctness (Accuracy)**: Testers will run a set of 50 core catalog queries. Accuracy on course prerequisites and transfer policies must be **100% compliant** with official catalogs.
> 3. **Responsiveness (UI/UX)**: The widget must render perfectly on both mobile screens (Chrome/Safari) and desktop sizes, never covering important site controls.
