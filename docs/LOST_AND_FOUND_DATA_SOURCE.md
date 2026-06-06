# Lost & Found Data Source & Integration Brief (Issue #14)

This document analyzes the existing infrastructure for Lost & Found management at Dallas College and presents the integration strategy for the chatbot.

---

## 1. Operational Realities of Dallas College Lost & Found

Unlike academic courses or public calendars, Dallas College **does not maintain a public online database or real-time API listing active lost items**. 

Instead, the process is handled physically and administratively on a campus-by-campus basis:
1.  **Administrative Ownership**: Centralized within the **Office of Student Life and Engagement** at each of the seven campuses.
2.  **High-Value Items**: High-value items (e.g., laptops, phones, wallets) are secured in cooperation with the **Dallas College Police Department**.
3.  **No Public Listings**: The registry of lost items is kept in internal spreadsheets or logs managed by Student Life staff.

---

## 2. Campus Directory & Routing Map

The chatbot integrates a static knowledge base directory to instantly provide room locations, phone numbers, and email channels for each campus:

| Campus | Physical Office (Student Life) | Phone Number | Contact Email |
| :--- | :--- | :--- | :--- |
| **Brookhaven** | Building S, Room S251 | 972-860-4115 | `studentlife@dallascollege.edu` |
| **Cedar Valley** | Building D, Room D104 | 972-860-8233 | `studentlife@dallascollege.edu` |
| **Eastfield** | Building B, Room B1100 | 972-391-1099 | `studentlife@dallascollege.edu` |
| **El Centro** | Building B, Room B270 | 214-860-2137 | `studentlife@dallascollege.edu` |
| **Mountain View** | Building S, Room S1032 | 214-860-8685 | `studentlife@dallascollege.edu` |
| **North Lake** | Building H, Room H201 | 972-273-3020 | `studentlife@dallascollege.edu` |
| **Richland** | Building E, Room E040 | 972-238-6130 | `studentlife@dallascollege.edu` |

---

## 3. Chatbot Integration & Triage Strategy

Since a direct database query is not possible, we propose a two-phase chatbot flow:

### Phase A: Knowledge Retrieval & Routing (Static)
*   **Trigger**: User asks *"I lost my keys at Richland"* or *"Where is lost and found at Eastfield?"*.
*   **Behavior**: The chatbot pulls from the static directory and provides the exact room number, phone number, and instructions to visit the Office of Student Life and Engagement.

### Phase B: Moderated Intake Flow (Interactive)
*   **Trigger**: User requests to report a lost or found item.
*   **Behavior**:
    1.  The chatbot prompts the user for:
        *   Item description (e.g., color, brand).
        *   Location where it was lost/found.
        *   Approximate date/time.
        *   Student contact email.
    2.  The backend triggers a secure webhook to email the intake form to the corresponding Student Life Office email (e.g., `richlandcoaching@dallascollege.edu` or the central `studentlife@dallascollege.edu` with subject header `[Chatbot Lost & Found Report]`).
    3.  A staff member can then match the report against their physical logs.
