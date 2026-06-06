# User Personas: Success Coach Chatbot (Issue #6)

This document defines the primary user personas for the Dallas College Success Coach Chatbot. These personas guide design decisions, functional priorities, and the AI's system persona ("Ali").

---

## 1. Persona Overview

To build an empathetic and effective chatbot, we focus on three distinct user types:
1. **The First-Generation Student**: Needs clear, jargon-free guidance and mobile-first access.
2. **The Non-Traditional/Part-Time Student**: Needs 24/7 access to scheduling, deadlines, and policy information.
3. **The Success Coach (Advisor)**: Needs students to be pre-informed on basic requirements so advising sessions can focus on high-value guidance.

---

## 2. Persona Profiles

### 👤 Persona A: Mateo Rodriguez (First-Gen Transfer Student)
*   **Role**: Student
*   **Location**: Richland Campus (taking hybrid classes)
*   **Academic Path**: Associate of Science (AS) in Computer Science, aiming to transfer to UT Dallas.
*   **Background**: 19 years old, first-generation college student. Works 20 hours/week at a local retail store.

#### Goals & Motivations
- Verify which classes (like COSC 1436 and MATH 2413) transfer directly to UTD.
- Keep track of FAFSA priority deadlines without missing critical dates.
- Access free tutoring for math and programming during late-night study sessions.

#### Pain Points & Frustrations
- Overwhelmed by navigating complex Dallas College websites (eConnect vs. Navigate).
- Unfamiliar with academic jargon (e.g., "TSI complete", "census date", "articulation agreement").
- Limited time during business hours to visit physical advising offices.

#### Chatbot Interaction Scenario
*Mateo opens the chatbot on his phone late at night:*
> **Mateo:** "Does COSC 1437 transfer to UTD for Computer Science?"
> **Ali (AI):** "Yes, COSC 1437 (Programming Fundamentals II) transfers directly to UT Dallas as CS 1337! You will need a grade of 'C' or better to transfer the credits. Would you like a link to the complete UTD CS transfer guide?"

---

### 👤 Persona B: Sarah Jenkins (The Overburdened Success Coach)
*   **Role**: Academic Advisor / Success Coach
*   **Location**: Sabine Hall, Richland Campus
*   **Background**: 34 years old, has worked as an academic advisor for 6 years. Manages a caseload of over 350 students.

#### Goals & Motivations
- Spend session time on high-impact career pathing and academic interventions rather than repeating basic policies.
- Ensure students come to appointments prepared with their core questions already answered.
- Have a reliable tool she can point students to for quick lookups (e.g., parking registration, building hours).

#### Pain Points & Frustrations
- Spends 8% of her time answering repetitive questions about FAFSA codes, TSI holds, and add/drop dates.
- Sees high appointment cancellation rates because students get stuck in long queues.
- Hard to keep track of real-time policy updates across seven different campuses.

#### Chatbot Interaction Scenario
*Sarah recommends the chatbot to students during orientation:*
> **Sarah:** "Use the chatbot to look up campus building codes, TSI status criteria, and transfer guides so that when you meet with me, we can jump straight into building your customized graduation roadmap."

---

### 👤 Persona C: Linda Chen (Non-Traditional Evening Student)
*   **Role**: Student / Working Parent
*   **Location**: Cedar Valley Campus (taking evening classes)
*   **Academic Path**: AAS in Business Management (Level 1 Certificate)
*   **Background**: 29 years old, returning to school after a 5-year break. Works full-time during the day and has a 4-year-old child.

#### Goals & Motivations
- Complete her Level 1 Certificate within two semesters to qualify for a promotion at work.
- Find child care or evening student services on campus.
- Easily set up a monthly payment plan for tuition before the billing deadline.

#### Pain Points & Frustrations
- Can only study after 8:00 PM when campuses and phone lines are closed.
- Hard to locate offices on campus since she only arrives after dark.
- Unclear how to submit tax transcripts or TASFA documents electronically.

#### Chatbot Interaction Scenario
*Linda uses the chatbot after her child is asleep:*
> **Linda:** "How do I set up a payment plan for summer classes?"
> **Ali (AI):** "You can set up an installment payment plan through Nelnet via eConnect! It splits your tuition into 3 or 4 monthly payments with a $35 setup fee. You must enroll before the tuition payment deadline. Would you like me to walk you through the steps on eConnect?"

---

## 3. Key Design Principles Derived from Personas

1.  **Jargon Fallback**: If the AI mentions a technical term like "TSI" or "Census Date", it should briefly define it or offer a citation link explaining it.
2.  **Encouraging Tone**: Since many users are first-generation or returning students, the chatbot should use warm, guiding language that builds confidence.
3.  **Actionable Citations**: Every policy response must include direct links (e.g., `[1]`, `[2]`) pointing to official Dallas College pages so students can confirm details and take the next step immediately.
