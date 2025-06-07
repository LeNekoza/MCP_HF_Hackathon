Here's a clear Markdown plan that outlines how to fix the chatbot so it **retrieves** and returns data instead of explaining how to do it:

---

# 🔧 Chatbot Data Retrieval Fix Plan

## 🎯 Objective

Update the chatbot so it directly **retrieves live data from the database** (e.g., total oxygen tanks) instead of just explaining the SQL logic or providing hypothetical responses.

## 🧩 Current Issue

When a user asks:

> *"Provide me total count of oxygen tank"*

The chatbot currently **describes** how the data would be queried, but **does not execute** the query or return real values.

## ✅ Solution

Enable the chatbot to:

1. **Parse the user question**
2. **Use schema context** (from `hospital_schema_guide.md`)
3. **Generate the appropriate SQL query**
4. **Run the query against the connected database**
5. **Return the actual result as a chatbot message**

## 🗂️ Files to Edit (inside `src/` folder)

* `src/interface.py`

  * Integrate logic to execute generated SQL against the database
  * Safely handle query input and prevent SQL injection
* `src/database.py` *(if exists)* or create one

  * Add a helper function to run SQL and return results
* `src/chatbot.html` – No change needed unless adding loading indicators

## 🔐 Security Notes

* Sanitize all dynamic SQL using parameterized queries
* Log query attempts and handle errors gracefully
* Ensure read-only access where appropriate

## 💡 Example Workflow

1. **User:** “What is the total count of oxygen tanks?”
2. **Bot internally:**

   ```sql
   SELECT SUM(quantity_total) FROM hospital_inventory WHERE item_type = 'oxygen_tank';
   ```
3. **Bot response:**

   > “The total number of oxygen tanks in inventory is: **250**.”

---
