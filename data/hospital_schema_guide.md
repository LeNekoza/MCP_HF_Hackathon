# 🏥 Hospital Data Schema & Query Guide

> **Purpose**
>
> This markdown document provides Large Language Models (LLMs) with the structural context they need to interpret end‑user questions about hospital data—**even when users omit explicit table names.** Keep this file in the system prompt or as a reference chunk so the model can reason about where each data point lives.

---

## 1. Datasets at a Glance

| Table (CSV file)     | Row count\* | Primary Key | Brief Purpose                                                    |
| -------------------- | ----------: | ----------- | ---------------------------------------------------------------- |
| `users`              |       3 210 | `id`        | All people in the system (patients **and** staff)                |
| `patient_records`    |       3 000 | `id`        | One row per patient medical profile; links to **users**          |
| `rooms`              |         150 | `id`        | Physical rooms/wards with static attributes                      |
| `occupancy`          |       1 100 | `id`        | Historical log of which patient occupied which room/bed and when |
| `storage_rooms`      |          50 | `id`        | Storage locations for supplies and equipment                     |
| `hospital_inventory` |         100 | `id`        | Consumables (e.g. blood units, oxygen) stored in `storage_rooms` |
| `tools`              |         500 | `id`        | Re‑usable medical equipment (infusion pumps, monitors, …)        |

\*Row counts are approximate as of the CSV snapshots included with this documentation.

---

## 2. Detailed Table Schemas

### 2.1 `users`

| Column              | Type                              | Notes                                        |
| ------------------- | --------------------------------- | -------------------------------------------- |
| `id`                | `BIGINT`                          | Primary key                                  |
| `full_name`         | `VARCHAR(255)`                    |                                              |
| `email`             | `VARCHAR(255)`                    | Unique                                       |
| `phone_number`      | `JSONB`                           | `{ "primary": "+91…", "type": "mobile" }`    |
| `emergency_contact` | `JSONB`                           | `{ "name": …, "phone": … }`                  |
| `password_hash`     | `TEXT`                            |                                              |
| `role`              | `ENUM('patient','staff','admin')` |                                              |
| `staff_type`        | `VARCHAR`                         | e.g. *doctor*, *nurse* (only for staff rows) |

---

### 2.2 `patient_records`

| Column              | Type                                              | Notes                                          |
| ------------------- | ------------------------------------------------- | ---------------------------------------------- |
| `id`                | `BIGINT`                                          | PK                                             |
| `user_id`           | `BIGINT`                                          | FK → `users.id`                                |
| `date_of_birth`     | `DATE`                                            | *DD‑MM‑YYYY* format in CSV                     |
| `gender`            | `CHAR(1)`                                         | `M` / `F`                                      |
| `blood_group`       | `ENUM('A+','A−','B+','B−','O+','O−','AB+','AB−')` |                                                |
| `allergies`         | `TEXT`                                            | Free text; comma‑separated list                |
| `medical_history`   | `TEXT / JSONB`                                    |                                                |
| `emergency_contact` | `JSONB`                                           | Overrides `users.emergency_contact` if present |
| `contact_phone`     | `JSONB`                                           | Overrides `users.phone_number` if present      |

> **🔑 Blood group counts live here.** For a question like “*How many B+ do we have?*” default to counting rows in `patient_records` where `blood_group = 'B+'`.

---

### 2.3 `rooms`

| Column              | Type      | Notes                             |
| ------------------- | --------- | --------------------------------- |
| `id`                | `BIGINT`  | PK                                |
| `room_number`       | `VARCHAR` | Human‑readable code (e.g. *R205*) |
| `room_type`         | `VARCHAR` | *ICU*, *General*, *Pediatric*, …  |
| `bed_capacity`      | `INT`     |                                   |
| `table_count`       | `INT`     | Side tables/desks                 |
| `has_oxygen_outlet` | `BOOLEAN` |                                   |
| `floor_number`      | `INT`     |                                   |
| `notes`             | `TEXT`    |                                   |
| `Unnamed:*`         | *NULL*    | CSV artefacts—ignore              |

---

### 2.4 `occupancy`

| Column               | Type        | Notes                                              |
| -------------------- | ----------- | -------------------------------------------------- |
| `id`                 | `BIGINT`    | PK                                                 |
| `room_id`            | `BIGINT`    | FK → `rooms.id`                                    |
| `bed_number`         | `INT`       |                                                    |
| `patient_id`         | `BIGINT`    | FK → `users.id` (only rows where `role='patient'`) |
| `attendee`           | `JSONB`     | Primary nurse / physician, shift info              |
| `assigned_at`        | `TIMESTAMP` | *DD‑MM‑YYYY HH\:MM*                                |
| `discharged_at`      | `TIMESTAMP` | May be `NULL` if ongoing                           |
| `tools`              | `JSONB`     | Equipment assigned during stay                     |
| `hospital_inventory` | `JSONB`     | Consumables allocated                              |
| `Unnamed:*`          | *NULL*      | Ignore                                             |

---

### 2.5 `storage_rooms`

| Column           | Type      | Notes                                        |
| ---------------- | --------- | -------------------------------------------- |
| `id`             | `BIGINT`  | PK                                           |
| `storage_number` | `VARCHAR` | Code e.g. *ST20001*                          |
| `storage_type`   | `VARCHAR` | *Medical Equipment Storage*, *Blood Bank*, … |
| `floor_number`   | `INT`     |                                              |
| `capacity`       | `INT`     | Max items                                    |
| `notes`          | `TEXT`    |                                              |
| `Unnamed:*`      | *NULL*    | Ignore                                       |

---

### 2.6 `hospital_inventory`

| Column                 | Type                                                           | Notes                                  |
| ---------------------- | -------------------------------------------------------------- | -------------------------------------- |
| `id`                   | `BIGINT`                                                       | PK                                     |
| `item_name`            | `VARCHAR`                                                      | *Blood Type O− 1*, *Oxygen Cylinder 3* |
| `item_type`            | `ENUM('blood_unit','oxygen_tank','medicine','misc_equipment')` |                                        |
| `quantity_total`       | `INT`                                                          | Total on hand                          |
| `quantity_available`   | `INT`                                                          | Currently unused                       |
| `location_storage_id`  | `BIGINT`                                                       | FK → `storage_rooms.id`                |
| `location_description` | `VARCHAR`                                                      | Mirrors `storage_rooms.storage_type`   |
| `details`              | `TEXT`                                                         |                                        |
| `expiry_date`          | `DATE`                                                         | Blood & meds only                      |

> **🔑 Blood *inventory* counts live here.** For “*How many B+ blood bags are in stock?*” filter `item_type='blood_unit'` and pattern‑match `item_name`.

---

### 2.7 `tools`

| Column                  | Type      | Notes                       |
| ----------------------- | --------- | --------------------------- |
| `id`                    | `BIGINT`  | PK                          |
| `tool_name`             | `VARCHAR` |                             |
| `description`           | `TEXT`    |                             |
| `category`              | `VARCHAR` | *Surgical*, *Diagnostic*, … |
| `quantity_total`        | `INT`     |                             |
| `quantity_available`    | `INT`     |                             |
| `location_storage_id`   | `BIGINT`  | FK → `storage_rooms.id`     |
| `location_description`  | `VARCHAR` |                             |
| `purchase_date`         | `DATE`    |                             |
| `last_maintenance_date` | `DATE`    |                             |
| `Unnamed:*`             | *NULL*    | Ignore                      |

---

## 3. Inter‑Table Relationships (Text Diagram)

```
users ─┬─< patient_records
       │      ▲
       │      │
       │   occupancy >── rooms
       │
       └─< occupancy

storage_rooms ──< hospital_inventory
storage_rooms ──< tools
```

* **Arrow key**: `A ─< B` means *A* has one‑to‑many relationship with *B* (i.e. `B` stores the foreign key).

---

## 4. Query Interpretation Rules for the LLM

1. **Blood group counts** → `patient_records.blood_group`.
2. **Blood unit stock** → `hospital_inventory` where `item_type='blood_unit'`.
3. **Room capacity/availability** → join `rooms` and `occupancy`.
4. **Equipment availability** → `tools.quantity_available`.
5. Always check for `role='patient'` when joining `users` to medical tables.

---

## 5. Data Quality & Parsing Notes

* **Date formats** vary: `DATE` columns use *DD‑MM‑YYYY*; `TIMESTAMP` uses *DD‑MM‑YYYY HH\:MM*.
* Columns named `Unnamed:*` are artefacts—ignore.
* Some JSONB columns store nested objects; parse them before field‑level filtering.

---

*Last updated:* 7 June 2025 (Asia/Kolkata)

---

### ✨ Usage Example for an LLM

> **User:** *How many B+ do we have?*
>
> **LLM reasoning:**
>
> 1. Ambiguous term “B+” → most likely **blood group**.
> 2. Blood groups stored in `patient_records.blood_group`.
> 3. Construct query A (see §5) and return count.
>
> *(If the user explicitly mentions *blood bags*, switch to query B.)*

---

### License

Internal hospital analytics only. Not for external distribution.
