# Foundational Concepts: HTML, JSON, SQL, and Scraping
> **Title**: Technical Primer for AI Club Members
> **Status**: COMPLETED PRIMER
> **Target Audience**: Success Coach Chatbot Engineering Team & Club Contributors

This document explains the core technical building blocks of our academic data ingestion pipeline: **HTML Parsing**, **JSON Data Structures**, and **SQL Relational Databases**. Understanding these three concepts is essential to contributing to the Success Coach chatbot's data engine.

---

## 1. HTML & Web Scraping (How We Get the Data)

### What is HTML?
HTML (HyperText Markup Language) is the structural skeleton of every web page. It is not a programming language; it is a markup language composed of **elements** that tell the browser how to display content.

An element consists of:
1. An **Opening Tag** (e.g., `<a href="...">`)
2. **Attributes** (extra metadata like classes, IDs, or links)
3. **Content** (text or other tags inside)
4. A **Closing Tag** (e.g., `</a>`)

```html
<a href="https://concourse.dallascollege.edu/syllabus/public/187654" class="syllabus-link">Class Syllabus</a>
```

### Core HTML Elements Used in Scraping
* `<table>`, `<tr>`, `<td>`, `<th>`: HTML tables.
  * `<tr>` = Table Row (horizontal line of cells).
  * `<td>` = Table Data (individual cells inside a row).
  * `<th>` = Table Header (bold labels at the top of a column).
* `<a>`: Anchor tag, used for links. The link itself is stored in the `href` attribute.
* `<div>`: A generic container used to group elements together. Often styled with classes.
* `<h1>`, `<h2>`, `<h3>`: Heading tags. Used to divide the document into sections (critical for chunking).

### CSS Selectors & Parsing (BeautifulSoup)
Web scrapers read raw HTML as a giant string. To make sense of it, we use libraries like **BeautifulSoup** in Python. We locate specific pieces of data using **CSS Selectors** (rules that target elements based on their tags, classes, or IDs):

1. **Tag Selection**: Target elements by their name (e.g., `find('tr')` finds the first table row).
2. **Class Selection (`.`)**: Target elements with specific style classes (e.g., `find_all('tr', class_='class-row')` finds all rows that represent a course section).
3. **Attribute Selection**: Target elements based on specific attributes (e.g., finding the `href` link inside a cell).

#### BeautifulSoup Concept Example:
If we have this HTML:
```html
<td class="class-instructor">
  <a href="https://concourse.dallascollege.edu/syllabus/public/12456/cv">Dr. Malone / Vita</a>
</td>
```
In Python, we parse it like this:
```python
# 1. Find the table cell with the class 'class-instructor'
instructor_cell = soup.find('td', class_='class-instructor')

# 2. Extract the anchor element inside that cell
link_element = instructor_cell.find('a')

# 3. Get the text and the link destination
instructor_name = link_element.text.replace('/ Vita', '').strip() # 'Dr. Malone'
cv_url = link_element['href']                                   # 'https://concourse.dallascollege.edu/syllabus/public/12456/cv'
```

---

## 2. JSON: JavaScript Object Notation (How We Structure the Data)

### What is JSON?
JSON is a lightweight, human-readable text format used to store and exchange data. Think of it as a dictionary or a structured map.

It supports two main structures:
1. **Objects (`{ }`)**: A collection of key-value pairs. Keys are always strings, followed by a colon and a value.
2. **Arrays (`[ ]`)**: An ordered list of values (which can be numbers, strings, objects, or other arrays).

### Data Types in JSON
* **String**: `"COSC-1436"`
* **Number**: `4` or `19.99`
* **Boolean**: `true` or `false`
* **Null**: `null` (empty value)
* **Array**: `["Math", "Science", "History"]`
* **Object**: Nested key-value pairs.

### Success Coach Schema Example
Below is how we represent a course mapping in JSON. Notice how a single **Course** object contains an array of **Section** objects, which nestedly contain the syllabus details:

```json
{
  "course_code": "COSC-1436",
  "course_name": "Programming Fundamentals I",
  "credit_hours": 4,
  "sections": [
    {
      "section_number": "11001",
      "term": "2026Summer",
      "instructor": {
        "name": "Dr. Malone",
        "email": "jmalone@dallascollege.edu"
      },
      "textbooks": [
        {
          "title": "Starting Out with C++",
          "required": true
        }
      ]
    }
  ]
}
```

---

## 3. SQL: Structured Query Language (How We Save the Data)

### What is SQL?
SQL is the standard language used to interact with Relational Database Management Systems (like PostgreSQL/Neon). In a relational database, data is saved in **Tables** (which look like spreadsheets with defined columns and dynamic rows).

### Core Database Relationships
To avoid repeating data (e.g., saving the same course description 50 times for 50 different sections), we divide data into separate tables and link them:

* **Primary Key (PK)**: A unique identifier for every row in a table (e.g., `course_id`).
* **Foreign Key (FK)**: A column in one table that links to the Primary Key of another table (e.g., `section_id` in our `course_chunks` table links back to the `course_sections` table).

### Core SQL Operations
Here are the SQL statements used in our ingestion script:

#### 1. Creating Tables (`CREATE TABLE`)
Defines the schema structure, data types, and relationship constraints.
```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,                    -- Auto-incrementing integer (Primary Key)
    course_code VARCHAR(20) UNIQUE NOT NULL, -- e.g., 'COSC-1436' (must be unique)
    course_name VARCHAR(255) NOT NULL,       -- String up to 255 chars
    credit_hours INT NOT NULL                 -- Integer
);
```

#### 2. Saving/Inserting Data (`INSERT INTO ... ON CONFLICT`)
Inserts new rows. Since we run scrapers periodically, we use "Upsert" (Update-Insert) logic. If a record already exists, we update it instead of crashing.
```sql
INSERT INTO courses (course_code, course_name, credit_hours)
VALUES ('COSC-1436', 'Programming Fundamentals I', 4)
ON CONFLICT (course_code) 
DO UPDATE SET course_name = EXCLUDED.course_name;
```

#### 3. Querying Data (`SELECT`)
Retrieves data from the database.
```sql
-- Retrieve all sections taught by Dr. Malone
SELECT section_code, term, campus 
FROM course_sections 
WHERE instructor_id = (SELECT id FROM instructors WHERE name = 'Dr. Malone');
```

---

## 4. How the Pipeline Connects Everything

The entire academic data flow works as a sequence:

```
[Web Schedules / Syllabi]
      │ (HTML Pages)
      ▼
[BeautifulSoup Parser]  <--- Targets tags (<tr>, <td>) & extracts text
      │ (Structured Dictionary)
      ▼
[JSON Payload]          <--- Organizes raw content into course-section relationships
      │ (API Output)
      ▼
[Neon PostgreSQL DB]    <--- Saves data into SQL Tables (courses, sections, chunks)
```

1. **Scrape**: The Python script downloads the schedule HTML from eConnect and individual syllabi from Concourse.
2. **Parse**: BeautifulSoup extracts the section numbers, textbook titles, and grading criteria.
3. **Format**: The script converts the parsed data into JSON structure to validate it.
4. **Insert**: The script connects to Neon PostgreSQL and executes SQL queries to save the data.
5. **RAG Vector Search**: For syllabus content, we generate a mathematical representation (a vector embedding) of the text and store it in Neon. When a student asks the chatbot a question, the Next.js backend performs a vector similarity search in SQL to fetch only the relevant syllabus chunk.
