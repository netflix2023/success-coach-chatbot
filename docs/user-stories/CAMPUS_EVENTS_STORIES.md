# User Stories: Campus Events & Deadlines (Issue #2)
> **Track**: Workshops, Club Schedules, and Academic Calendars

---

## Story 1: FAFSA / TASFA Assistance Workshops
### **As a** student needing financial aid assistance,
### **I want to** ask the chatbot for upcoming FAFSA / TASFA workshops,
### **So that** I can attend a session and receive hands-on help from financial aid advisors.

#### **Acceptance Criteria**:
1. The chatbot must search scraped general pages and calendars for financial aid workshops.
2. The response must list dates, times, and specific campus room locations (e.g., "Richland Campus, Room T160").
3. The chatbot must provide a contact email or phone number for the campus financial aid office.
4. If no workshops are currently scheduled, it must direct the user to the online financial aid scheduler tool.

---

## Story 2: Discovering Student Club Meetings
### **As a** new student seeking community,
### **I want to** ask about active student club meetings (e.g., "When does the AI Club meet?"),
### **So that** I can join and participate in extracurricular events.

#### **Acceptance Criteria**:
1. The chatbot must list matching student organization details, including meeting times and location coordinates.
2. The chatbot must display the club advisor's name and contact email if available in the directory metadata.
3. If the query does not yield any active clubs, it must display the Student Life department contact link.

---

## Story 3: Critical Academic Deadlines
### **As a** student managing course enrollments,
### **I want to** ask the chatbot for key calendar dates (e.g., "What is the last day to drop a class for a W?"),
### **So that** I can make academic adjustments without affecting my GPA.

#### **Acceptance Criteria**:
1. The chatbot must pull from the scraped Academic Calendar database to locate the exact drop/withdrawal deadline for the current semester.
2. The response must state the specific calendar date (e.g., "November 14, 2026").
3. The chatbot must warn the student about financial aid implications and suggest talking to an advisor: *"Dropping a class may affect your FAFSA eligibility. Please consult with an advisor before finalizing."*
