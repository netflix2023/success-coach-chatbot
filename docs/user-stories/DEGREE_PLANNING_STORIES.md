# User Stories: Degree & Program Planning (Issue #2)
> **Track**: Degree Planning, Prerequisites Check, and University Transfer

---

## Story 1: Cyber Security AAS Degree Requirements
### **As a** student planning my academic semester,
### **I want to** query the chatbot for the complete requirements of the Associate of Applied Science (AAS) in Cybersecurity,
### **So that** I know exactly which courses I must enroll in to graduate.

#### **Acceptance Criteria**:
1. The chatbot must list all core course prefixes and numbers (e.g., COSC-1436, ITSY-1300) required for the degree.
2. The response must state the total credit hours needed (60 credits).
3. The response must output a clickable citation link pointing directly to the official Dallas College program catalog URL.
4. Response latency must be under 1.2 seconds.

---

## Story 2: Instant Course Prerequisite Verification
### **As a** campus Success Coach / Advisor,
### **I want to** ask the chatbot for the prerequisites of a specific course (e.g., COSC-1437 or MATH-2413),
### **So that** I can instantly clear a student for enrollment without opening the heavy PDF catalog.

#### **Acceptance Criteria**:
1. The chatbot must retrieve the exact prerequisites (e.g., "Prerequisite: COSC-1436 with a grade of C or better") from the database.
2. If the course has no prerequisites, the bot must state: *"There are no official prerequisites for this course."*
3. Every prerequisite course code must be highlighted, and a catalog reference link must be attached.
4. The output must match the official Dallas College course description catalog database with 100% accuracy.

---

## Story 3: UT Dallas Computer Science Transfer Articulation
### **As a** transfer-bound student,
### **I want to** search for UTD Computer Science transfer articulation agreements,
### **So that** I can verify which Dallas College courses are guaranteed to transfer toward my bachelor's degree.

#### **Acceptance Criteria**:
1. The chatbot must search the database for transfer plans matching "UTD" or "University of Texas at Dallas" and "Computer Science".
2. It must provide a summary of the recommended transfer courses (e.g., MATH-2413, COSC-2436).
3. The response must direct the student to the official Dallas College transfer office directory and link to the UTD transfer guide page.
4. If details are missing, it must output a fallback message directing the student to the Richland campus transfer advisor.
