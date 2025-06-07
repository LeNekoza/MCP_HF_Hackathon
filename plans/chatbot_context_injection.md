Here’s a clear Markdown plan describing the update to the chatbot flow to include contextual grounding from the provided hospital schema document:

---

# 🧠 Chatbot Context Injection Plan

## 🎯 Objective

Update the existing **chatbot flow** to include **context from the `hospital_schema_guide.md` document** before generating **dynamic SQL queries**.

## 🧩 Problem

Currently, the chatbot generates SQL queries without structured awareness of how hospital data is organized. This can lead to:

* Incorrect or inefficient query generation
* Misinterpretation of ambiguous terms (e.g., “B+” meaning blood group vs. blood inventory)
* Poor schema alignment when users omit table names

## ✅ Solution

Inject the **contents of `hospital_schema_guide.md`** into the chatbot’s reasoning pipeline **before query generation**, so that the LLM:

* Understands available tables, columns, and relationships
* Applies interpretation rules (e.g., where blood group data resides)
* Uses schema-aware logic when constructing SQL

## 🗂️ Files to Edit (inside `src/` folder)

* `src/components/interface.py` – Modify the logic to:

  * Load the schema context at startup or per session
  * Prepend or embed it in the system message before query generation
* `src/components/interface.py` – Optional edits if UI feedback is added
* At Root `data/hospital_schema_guide.md` – Store this file and read it into the chatbot prompt

## 🧩 Context Usage Method

* Load `hospital_schema_guide.md` as a reference chunk
* Inject as part of a **system prompt**, **pre-prompt**, or **context embedding** before every SQL-related user query
* Avoid repeating the document; use caching or memory where possible

## 💡 Notes

* Do not alter chatbot personality or other unrelated behaviors
* This does **not** modify the chatbot UI – it only affects backend reasoning
* Ensure schema updates (if any) can be reloaded without restarting the app

---
