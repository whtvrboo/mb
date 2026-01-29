# 🔍 Critical Analysis & Refined Data Model

## 🚨 CRITICAL GAPS IDENTIFIED

### 1. **Notification System - MISSING**

You have events that trigger notifications (expired warranties, pet vaccines, chore deadlines) but no infrastructure to deliver them.

**NEEDED:**

```
NotificationPreference
- user_id
- channel (EMAIL, PUSH, SMS, IN_APP)
- event_type (CHORE_DUE, EXPENSE_ADDED, VOTE_OPENED, etc.)
- enabled (Boolean)
- advance_notice_hours (Integer)

Notification
- id
- user_id
- type (Enum)
- title
- body
- link_url
- is_read
- created_at
- delivered_at
```

### 2. **Audit Log - MISSING**

No way to see "who changed what when" - critical for dispute resolution.

**NEEDED:**

```
AuditLog
- id
- group_id
- user_id
- action (CREATED, UPDATED, DELETED, VIEWED)
- entity_type (EXPENSE, CHORE, PET, etc.)
- entity_id
- old_values (JSONB)
- new_values (JSONB)
- ip_address
- occurred_at
```

### 3. **Comments/Notes System - MISSING**

Users can't discuss expenses, chores, proposals in-app.

**NEEDED:**

```
Comment
- id
- author_id
- parent_type (EXPENSE, CHORE, PROPOSAL, PET, PLANT, ASSET)
- parent_id
- content (Text)
- is_edited
- created_at
- edited_at
- deleted_at

Reaction (Emoji reactions)
- id
- user_id
- comment_id
- emoji_code
```

### 4. **Recurring Expenses - INCOMPLETE**

You track one-time expenses but not subscriptions (Netflix, rent, utilities).

**NEEDED:**

```
RecurringExpense
- id
- group_id
- paid_by_user_id
- description
- amount
- currency_code
- category_id
- frequency_type (MONTHLY, WEEKLY, YEARLY)
- start_date
- end_date (nullable)
- next_due_date
- auto_create_expense (Boolean)
- is_active
```

### 5. **Budget System - MISSING**

No way to set spending limits per category.

**NEEDED:**

```
Budget
- id
- group_id
- category_id
- amount_limit
- currency_code
- period_type (WEEKLY, MONTHLY, YEARLY)
- start_date
- end_date (nullable)
- alert_threshold_percentage (default 80)
```

### 6. **Meal Planning Integration - WEAK**

Recipes exist but no calendar integration.

**NEEDED:**

```
MealPlan
- id
- group_id
- date
- meal_type (BREAKFAST, LUNCH, DINNER, SNACK)
- recipe_id (nullable)
- assigned_cook_id
- notes
- is_completed

MealPlanShoppingSync
- meal_plan_id
- list_id
- synced_at
```

### 7. **Gamification/Rewards - INCOMPLETE**

You have `effort_value` but no tracking of points/achievements.

**NEEDED:**

```
UserPoints
- id
- user_id
- group_id
- total_points
- monthly_points
- last_reset_at

Achievement
- id
- name
- description
- badge_icon_url
- points_required

UserAchievement
- id
- user_id
- achievement_id
- earned_at
```

### 8. **File Attachments - INSUFFICIENT**

Documents exist but not linked everywhere needed.

**NEEDED:**

- Add `attachment_id` to: ChoreAssignment, Item, PlantLog, Settlement

### 9. **Calendar/Events - MISSING**

No way to track birthdays, move-in dates, lease renewals.

**NEEDED:**

```
CalendarEvent
- id
- group_id
- created_by_id
- title
- description
- event_date
- event_time (nullable)
- reminder_days_before
- category (BIRTHDAY, LEASE, MAINTENANCE, SOCIAL)
- linked_user_id (for birthdays)
- linked_asset_id (for lease/maintenance)
```

### 10. **Split Settings Presets - MISSING**

No default split rules (equal, by income, custom percentages).

**NEEDED:**

```
SplitPreset
- id
- group_id
- name
- is_default
- method (EQUAL, PERCENTAGE, FIXED_AMOUNT, BY_INCOME)

SplitPresetMember
- id
- preset_id
- user_id
- percentage (nullable)
- fixed_amount (nullable)
```

---

## ✨ REFINED & COMPLETE DATA MODEL

### 1. 👥 **Core Identity & Access** (ENHANCED)

```sql
User
├── id (PK)
├── email (unique, indexed)
├── hashed_password
├── name (indexed)
├── avatar_url
├── phone_number ⭐ NEW
├── birth_date ⭐ NEW (for birthday reminders)
├── is_superuser
├── is_active
├── preferences (JSONB)
├── language_code (default "en") ⭐ NEW
├── created_at
├── last_login_at ⭐ NEW
└── deleted_at

Group
├── id (PK)
├── name
├── created_by_id (FK users)
├── default_currency (length=3, default "USD")
├── timezone (default "UTC")
├── avatar_url ⭐ NEW
├── description (Text) ⭐ NEW
├── address (Text) ⭐ NEW (for lease events)
├── lease_start_date ⭐ NEW
├── lease_end_date ⭐ NEW
├── landlord_contact_id (FK service_contacts) ⭐ NEW
├── created_at
└── deleted_at

UserGroup
├── id (PK)
├── user_id (FK users)
├── group_id (FK groups)
├── role (ADMIN, MEMBER, GUEST, CHILD)
├── nickname ⭐ NEW (group-specific display name)
├── joined_at
├── left_at ⭐ NEW (for history)
└── Constraint: Unique(user_id, group_id) where left_at is null

Invite
├── id (PK)
├── group_id (FK groups)
├── created_by_id (FK users)
├── code (unique, indexed)
├── email_hint
├── role (default MEMBER)
├── max_uses ⭐ NEW (default 1)
├── use_count ⭐ NEW (default 0)
├── expires_at
└── is_active

Location
├── id (PK)
├── group_id (FK groups)
├── name
├── floor_level
├── sunlight_direction (NORTH, SOUTH, EAST, WEST)
├── humidity_level (LOW, MEDIUM, HIGH) ⭐ NEW
├── temperature_avg_celsius ⭐ NEW
└── notes (Text) ⭐ NEW

ServiceContact
├── id (PK)
├── group_id (FK groups)
├── name
├── job_title (VET, PLUMBER, ELECTRICIAN, DOCTOR, LANDLORD, OTHER) ⭐ LANDLORD added
├── company_name ⭐ NEW
├── phone
├── email
├── address
├── website_url
├── emergency_contact (Boolean) ⭐ NEW
└── notes (Text) ⭐ NEW
```

---

### 2. 💸 **Finance & Settlements** (ENHANCED)

```sql
Category ⭐ NEW - YOU FORGOT THIS!
├── id (PK)
├── group_id (FK groups, nullable) -- null = global
├── name
├── icon_emoji
├── color_hex
├── parent_category_id (FK categories, nullable) -- For hierarchies
└── is_income (Boolean, default false)

Expense
├── id (PK)
├── group_id (FK groups)
├── paid_by_user_id (FK users)
├── description
├── amount
├── currency_code
├── exchange_rate (snapshot)
├── category_id (FK categories)
├── receipt_img_url
├── expense_date
├── payment_method (CARD, CASH, TRANSFER, OTHER) ⭐ NEW
├── vendor_name ⭐ NEW
├── is_reimbursable (Boolean) ⭐ NEW
├── is_recurring_generated (Boolean) ⭐ NEW
├── linked_proposal_id (FK proposals)
├── linked_pet_medical_id (FK pet_medical_records)
├── linked_maintenance_log_id (FK maintenance_logs)
├── linked_recurring_expense_id (FK recurring_expenses) ⭐ NEW
├── created_at ⭐ NEW
└── deleted_at

ExpenseSplit
├── id (PK)
├── expense_id (FK expenses)
├── user_id (FK users)
├── owed_amount
├── is_paid (Boolean, default false) ⭐ NEW
├── paid_at ⭐ NEW
└── manual_override

RecurringExpense ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── paid_by_user_id (FK users)
├── description
├── amount
├── currency_code
├── category_id (FK categories)
├── frequency_type (WEEKLY, MONTHLY, YEARLY, CUSTOM)
├── interval_value (Integer, default 1)
├── start_date
├── end_date (nullable)
├── next_due_date
├── auto_create_expense (Boolean, default true)
├── split_preset_id (FK split_presets) ⭐ NEW
└── is_active

Settlement
├── id (PK)
├── group_id (FK groups)
├── payer_id (FK users)
├── payee_id (FK users)
├── amount
├── currency_code
├── method (CASH, VENMO, ZELLE, BANK_TRANSFER) ⭐ NEW
├── settled_at
├── confirmation_code
└── notes (Text) ⭐ NEW

SplitPreset ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── name
├── is_default
└── method (EQUAL, PERCENTAGE, FIXED_AMOUNT, BY_INCOME)

SplitPresetMember ⭐ NEW
├── id (PK)
├── preset_id (FK split_presets)
├── user_id (FK users)
├── percentage (nullable)
└── fixed_amount (nullable)

Budget ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── category_id (FK categories)
├── amount_limit
├── currency_code
├── period_type (WEEKLY, MONTHLY, YEARLY)
├── start_date
├── end_date (nullable)
└── alert_threshold_percentage (default 80)

BalanceSnapshot ⭐ NEW (for performance)
├── id (PK)
├── group_id (FK groups)
├── user_id (FK users)
├── balance_amount
├── currency_code
├── snapshot_date
└── created_at
```

---

### 3. 🛒 **Inventory & Lists** (ENHANCED)

```sql
CommonItemConcept
├── id (PK)
├── name (unique)
├── default_category_id
├── barcode (String) ⭐ NEW (for scanning)
├── average_price ⭐ NEW
└── image_url ⭐ NEW

List
├── id (PK)
├── group_id (FK groups)
├── name
├── type (SHOPPING, TODO)
├── created_by_id (FK users) ⭐ NEW
├── deadline (DateTime) ⭐ NEW
├── store_name ⭐ NEW
├── estimated_total ⭐ NEW
├── is_archived
└── archived_at ⭐ NEW

Item
├── id (PK)
├── list_id (FK lists)
├── name
├── quantity_value
├── quantity_unit
├── concept_id (FK common_item_concepts)
├── is_checked
├── checked_at ⭐ NEW
├── price_estimate ⭐ NEW
├── priority (Enum: HIGH, MEDIUM, LOW) ⭐ NEW
├── added_by_id (FK users)
├── assigned_to_id (FK users)
├── attachment_id (FK documents) ⭐ NEW
└── notes (Text) ⭐ NEW

ListShare ⭐ NEW (share list with non-group members)
├── id (PK)
├── list_id (FK lists)
├── share_code (unique)
├── can_edit (Boolean)
├── expires_at
└── created_at

InventoryItem ⭐ NEW (pantry tracking)
├── id (PK)
├── group_id (FK groups)
├── location_id (FK locations)
├── concept_id (FK common_item_concepts)
├── quantity_value
├── quantity_unit
├── expiration_date ⭐ NEW
├── opened_date ⭐ NEW
└── restock_threshold ⭐ NEW (auto-add to list)
```

---

### 4. 🧹 **Chores & Tasks** (ENHANCED)

```sql
Chore
├── id (PK)
├── group_id (FK groups)
├── name
├── description
├── frequency_type (DAILY, WEEKLY, MONTHLY, CUSTOM, SEASONAL) ⭐ SEASONAL added
├── interval_value
├── effort_value
├── estimated_duration_minutes ⭐ NEW
├── category (CLEANING, OUTDOOR, MAINTENANCE, ADMIN, OTHER) ⭐ NEW
├── required_item_concept_id (FK common_item_concepts) ⭐ NEW
├── is_rotating
├── rotation_strategy (ROUND_ROBIN, LEAST_BUSY, RANDOM) ⭐ NEW
├── last_assigned_to_id (FK users) ⭐ NEW
├── is_active ⭐ NEW
└── created_at ⭐ NEW

ChoreAssignment
├── id (PK)
├── chore_id (FK chores)
├── assigned_to_id (FK users)
├── due_date
├── completed_at
├── completed_by_id (FK users)
├── status (PENDING, IN_PROGRESS, COMPLETED, SKIPPED) ⭐ IN_PROGRESS added
├── started_at ⭐ NEW
├── actual_duration_minutes ⭐ NEW
├── quality_rating (1-5) ⭐ NEW
├── rated_by_id (FK users) ⭐ NEW
├── attachment_id (FK documents) ⭐ NEW
└── notes (Text) ⭐ NEW

ChoreDependency ⭐ NEW (chore X must be done before Y)
├── id (PK)
├── chore_id (FK chores)
├── depends_on_chore_id (FK chores)
└── dependency_type (BLOCKING, SUGGESTED)

ChoreTemplate ⭐ NEW (marketplace/library of common chores)
├── id (PK)
├── name
├── description
├── frequency_type
├── interval_value
├── effort_value
├── category
├── is_public
└── use_count
```

---

### 5. 🗳️ **Governance (Voting)** (ENHANCED)

```sql
Proposal
├── id (PK)
├── group_id (FK groups)
├── created_by_id (FK users)
├── title
├── description
├── type (GENERAL, EXPENSE_REQUEST, POLICY_CHANGE, KICK_USER, CHORE_ASSIGNMENT, PET_ADOPTION) ⭐ 2 NEW
├── strategy (SIMPLE_MAJORITY, UNANIMOUS, RANKED_CHOICE, WEIGHTED) ⭐ WEIGHTED added
├── status (DRAFT, OPEN, PASSED, REJECTED, EXECUTED, CANCELLED) ⭐ CANCELLED added
├── deadline_at
├── min_quorum_percentage ⭐ NEW
├── linked_expense_id (FK expenses)
├── linked_chore_id (FK chores) ⭐ NEW
├── linked_pet_id (FK pets) ⭐ NEW
├── execution_result (JSONB) ⭐ NEW
└── executed_at ⭐ NEW

BallotOption
├── id (PK)
├── proposal_id (FK proposals)
├── text
├── display_order ⭐ NEW
├── metadata (JSONB)
└── vote_count ⭐ NEW (denormalized for performance)

VoteRecord
├── id (PK)
├── proposal_id (FK proposals)
├── user_id (FK users)
├── ballot_option_id (FK ballot_options)
├── rank_order ⭐ NEW (for ranked choice)
├── weight (default 1)
├── is_anonymous ⭐ NEW
└── voted_at

VoteDelegation ⭐ NEW (proxy voting)
├── id (PK)
├── group_id (FK groups)
├── delegator_id (FK users)
├── delegate_id (FK users)
├── topic_category (ALL, FINANCE, CHORES, PETS, etc.)
├── start_date
├── end_date (nullable)
└── is_active
```

---

### 6. 🌿 **Flora (Plants)** (ENHANCED)

```sql
PlantSpecies
├── id (PK)
├── scientific_name (unique)
├── common_name
├── toxicity (SAFE, TOXIC_CATS, TOXIC_DOGS, TOXIC_ALL)
├── light_needs (LOW, INDIRECT, DIRECT)
├── water_interval_summer
├── water_interval_winter
├── humidity_preference (LOW, MEDIUM, HIGH) ⭐ NEW
├── fertilize_frequency_weeks ⭐ NEW
├── growth_rate (SLOW, MEDIUM, FAST) ⭐ NEW
├── mature_height_cm ⭐ NEW
├── propagation_method (SEED, CUTTING, DIVISION) ⭐ NEW
└── care_difficulty (EASY, MODERATE, HARD) ⭐ NEW

Plant
├── id (PK)
├── group_id (FK groups)
├── species_id (FK plant_species)
├── location_id (FK locations)
├── nickname
├── acquired_at
├── acquired_from (STORE, GIFT, PROPAGATION) ⭐ NEW
├── parent_plant_id (FK plants) ⭐ NEW (for propagation tracking)
├── pot_size_cm ⭐ NEW
├── photo_url
├── is_alive
├── died_at ⭐ NEW
├── death_reason ⭐ NEW
└── notes (Text) ⭐ NEW

PlantLog
├── id (PK)
├── plant_id (FK plants)
├── user_id (FK users)
├── action (WATER, FERTILIZE, PRUNE, REPOT, PEST_CONTROL, ROTATE, PROPAGATE) ⭐ 2 NEW
├── quantity_value ⭐ NEW (ml of water, etc.)
├── quantity_unit ⭐ NEW
├── notes
├── photo_url ⭐ NEW (progress photos)
└── occurred_at

PlantSchedule ⭐ NEW (next actions)
├── id (PK)
├── plant_id (FK plants)
├── action_type (WATER, FERTILIZE, etc.)
├── next_due_date
├── frequency_days
└── assigned_to_id (FK users)
```

---

### 7. 🐾 **Fauna (Pets)** (ENHANCED)

```sql
Pet
├── id (PK)
├── group_id (FK groups)
├── name
├── species (DOG, CAT, BIRD, REPTILE, FISH, RODENT, OTHER) ⭐ FISH, RODENT added
├── breed
├── sex (MALE, FEMALE, UNKNOWN) ⭐ NEW
├── date_of_birth
├── adoption_date ⭐ NEW
├── chip_id
├── weight_kg ⭐ NEW
├── color_markings ⭐ NEW
├── photo_url ⭐ NEW
├── vet_contact_id (FK service_contacts)
├── insurance_policy_number ⭐ NEW
├── insurance_provider ⭐ NEW
├── diet_instructions
├── medication_schedule (JSONB) ⭐ NEW
├── special_needs (Text) ⭐ NEW
├── is_alive ⭐ NEW
└── died_at ⭐ NEW

PetMedicalRecord
├── id (PK)
├── pet_id (FK pets)
├── type (VACCINE, SURGERY, CHECKUP, MEDICATION, INJURY, ALLERGY) ⭐ 2 NEW
├── description
├── performed_at
├── performed_by (String) ⭐ NEW (vet name)
├── cost_expense_id (FK expenses) ⭐ NEW
├── expires_at
├── reminder_days_before ⭐ NEW
├── document_id (FK documents)
└── notes (Text) ⭐ NEW

PetLog
├── id (PK)
├── pet_id (FK pets)
├── user_id (FK users)
├── action (WALK, FEED, MEDICINE, GROOM, PLAY, VET_VISIT) ⭐ 2 NEW
├── value_amount
├── value_unit ⭐ NEW
├── notes
├── photo_url ⭐ NEW
└── occurred_at

PetSchedule ⭐ NEW
├── id (PK)
├── pet_id (FK pets)
├── action_type (WALK, FEED, MEDICINE)
├── frequency_type (DAILY, WEEKLY)
├── time_of_day (TIME)
├── assigned_to_id (FK users)
├── is_rotating
└── is_active
```

---

### 8. 🏠 **Assets & Maintenance** (ENHANCED)

```sql
HomeAsset
├── id (PK)
├── group_id (FK groups)
├── location_id (FK locations)
├── name
├── asset_type (APPLIANCE, HVAC, PLUMBING, ELECTRICAL, FURNITURE, ELECTRONICS, OTHER) ⭐ NEW
├── brand ⭐ NEW
├── model_number ⭐ NEW
├── serial_number
├── purchase_date
├── purchase_price ⭐ NEW
├── purchase_store ⭐ NEW
├── warranty_end_date
├── warranty_type (MANUFACTURER, EXTENDED, NONE) ⭐ NEW
├── energy_rating ⭐ NEW
├── photo_url ⭐ NEW
├── manual_document_id (FK documents)
├── receipt_document_id (FK documents) ⭐ NEW
├── service_contact_id (FK service_contacts)
├── is_active ⭐ NEW
└── disposed_at ⭐ NEW

MaintenanceTask
├── id (PK)
├── asset_id (FK home_assets)
├── name
├── frequency_days
├── last_completed_at ⭐ NEW
├── next_due_date ⭐ NEW
├── priority (LOW, MEDIUM, HIGH, CRITICAL) ⭐ NEW
├── instructions
├── estimated_duration_minutes ⭐ NEW
├── estimated_cost ⭐ NEW
├── required_item_concept_id (FK common_item_concepts)
└── is_active ⭐ NEW

MaintenanceLog
├── id (PK)
├── task_id (FK maintenance_tasks)
├── user_id (FK users)
├── completed_at
├── actual_duration_minutes ⭐ NEW
├── cost_expense_id (FK expenses)
├── notes (Text) ⭐ NEW
├── photo_url ⭐ NEW
└── quality_rating ⭐ NEW

AssetInsurance ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── policy_number
├── provider_name
├── coverage_type (RENTERS, HOMEOWNERS, VEHICLE, OTHER)
├── premium_amount
├── premium_frequency (MONTHLY, YEARLY)
├── start_date
├── end_date
├── deductible_amount
└── document_id (FK documents)
```

---

### 9. 🔐 **Secrets & Files** (ENHANCED)

```sql
SharedCredential
├── id (PK)
├── group_id (FK groups)
├── name
├── credential_type (WIFI, STREAMING, BANK, UTILITY, OTHER) ⭐ NEW
├── username_identity
├── encrypted_password
├── access_level (ADMIN_ONLY, MEMBER, GUEST)
├── url
├── last_rotated_at ⭐ NEW
├── rotation_reminder_days ⭐ NEW
└── notes (Text) ⭐ NEW

Document
├── id (PK)
├── group_id (FK groups)
├── uploaded_by_id (FK users)
├── file_key (S3 Key)
├── file_name
├── mime_type
├── file_size_bytes
├── folder_path ⭐ NEW
├── tags (JSONB) ⭐ NEW
├── is_encrypted ⭐ NEW
├── created_at
└── deleted_at ⭐ NEW

DocumentShare ⭐ NEW
├── id (PK)
├── document_id (FK documents)
├── shared_with_user_id (FK users)
├── can_edit (Boolean)
├── expires_at
└── created_at
```

---

### 10. 🍽️ **Recipes & Meal Planning** (ENHANCED)

```sql
Recipe
├── id (PK)
├── group_id (FK groups)
├── owner_user_id (FK users)
├── title
├── description (Text) ⭐ NEW
├── cuisine_type ⭐ NEW
├── difficulty (EASY, MEDIUM, HARD) ⭐ NEW
├── prep_time_minutes
├── cook_time_minutes
├── servings
├── calories_per_serving ⭐ NEW
├── photo_url ⭐ NEW
├── source_url ⭐ NEW
├── is_favorite (Boolean) ⭐ NEW
└── times_cooked ⭐ NEW

RecipeIngredient
├── id (PK)
├── recipe_id (FK recipes)
├── name
├── quantity_value
├── quantity_unit
├── item_concept_id (FK common_item_concepts)
├── is_optional ⭐ NEW
└── preparation_note ⭐ NEW

RecipeStep ⭐ NEW
├── id (PK)
├── recipe_id (FK recipes)
├── step_number
├── instruction (Text)
├── duration_minutes
└── photo_url

MealPlan ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── date
├── meal_type (BREAKFAST, LUNCH, DINNER, SNACK)
├── recipe_id (FK recipes)
├── assigned_cook_id (FK users)
├── servings_planned
├── notes
└── is_completed

MealPlanShoppingSync ⭐ NEW
├── id (PK)
├── meal_plan_id (FK meal_plans)
├── list_id (FK lists)
└── synced_at
```

---

### 11. 📱 **Notifications & Communication** (NEW MODULE)

```sql
NotificationPreference ⭐ NEW
├── id (PK)
├── user_id (FK users)
├── event_type (CHORE_DUE, EXPENSE_ADDED, VOTE_OPENED, VACCINE_DUE, WARRANTY_EXPIRING, etc.)
├── channel (EMAIL, PUSH, SMS, IN_APP)
├── enabled (Boolean)
├── advance_notice_hours
└── quiet_hours_start (TIME)

Notification ⭐ NEW
├── id (PK)
├── user_id (FK users)
├── group_id (FK groups)
├── type (Enum)
├── title
├── body
├── link_url
├── priority (LOW, MEDIUM, HIGH)
├── is_read
├── read_at
├── created_at
└── delivered_at

Comment ⭐ NEW
├── id (PK)
├── author_id (FK users)
├── parent_type (EXPENSE, CHORE, PROPOSAL, PET, PLANT, ASSET, RECIPE)
├── parent_id
├── content (Text)
├── is_edited
├── created_at
├── edited_at
└── deleted_at

Reaction ⭐ NEW
├── id (PK)
├── user_id (FK users)
├── target_type (COMMENT, EXPENSE, CHORE_ASSIGNMENT)
├── target_id
├── emoji_code
└── created_at

Mention ⭐ NEW (for @username tagging)
├── id (PK)
├── comment_id (FK comments)
├── mentioned_user_id (FK users)
└── is_read
```

---

### 12. 📊 **Gamification & Achievements** (NEW MODULE)

```sql
UserPoints ⭐ NEW
├── id (PK)
├── user_id (FK users)
├── group_id (FK groups)
├── total_points
├── monthly_points
├── last_reset_at
└── rank_position

Achievement ⭐ NEW
├── id (PK)
├── name
├── description
├── badge_icon_url
├── category (CHORES, FINANCE, PLANTS, PETS)
├── requirement_type (POINTS, COUNT, STREAK)
├── requirement_value
└── is_active

UserAchievement ⭐ NEW
├── id (PK)
├── user_id (FK users)
├── achievement_id (FK achievements)
├── earned_at
└── progress_percentage

Streak ⭐ NEW
├── id (PK)
├── user_id (FK users)
├── group_id (FK groups)
├── activity_type (CHORES, PLANT_CARE, PET_CARE)
├── current_streak_days
├── longest_streak_days
└── last_activity_date

Leaderboard ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── period_type (WEEKLY, MONTHLY, ALL_TIME)
├── metric (POINTS, CHORES_COMPLETED, EXPENSES_ADDED)
├── period_start_date
└── period_end_date
```

---

### 13. 📅 **Calendar & Events** (NEW MODULE)

```sql
CalendarEvent ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── created_by_id (FK users)
├── title
├── description
├── event_date
├── event_time
├── end_time
├── is_all_day
├── category (BIRTHDAY, LEASE, MAINTENANCE, SOCIAL, HOLIDAY, OTHER)
├── recurrence_rule (RRULE string) ⭐ NEW
├── reminder_minutes_before
├── location_text ⭐ NEW
├── linked_user_id (FK users) -- for birthdays
├── linked_asset_id (FK home_assets) -- for maintenance
├── linked_pet_id (FK pets) -- for vet appointments
└── is_cancelled

EventAttendee ⭐ NEW
├── id (PK)
├── event_id (FK calendar_events)
├── user_id (FK users)
├── rsvp_status (YES, NO, MAYBE, PENDING)
└── rsvp_at

Reminder ⭐ NEW (general purpose)
├── id (PK)
├── group_id (FK groups)
├── user_id (FK users)
├── title
├── description
├── due_date
├── priority
├── is_completed
└── completed_at
```

---

### 14. 🔍 **Audit & Analytics** (NEW MODULE)

```sql
AuditLog ⭐ NEW
├── id (PK)
├── group_id (FK groups)
├── user_id (FK users)
├── action (CREATED, UPDATED, DELETED, VIEWED, APPROVED, REJECTED)
├── entity_type (EXPENSE, CHORE, PET, etc.)
├── entity_id
├── old_values (JSONB)
├── new_values (JSONB)
├── ip_address
├── user_agent
└── occurred_at

ReportSnapshot ⭐ NEW (pre-computed reports)
├── id (PK)
├── group_id (FK groups)
├── report_type (MONTHLY_EXPENSES, CHORE_COMPLETION, BUDGET_STATUS)
├── period_start_date
├── period_end_date
├── data_json (JSONB)
└── generated_at

Tag ⭐ NEW (universal tagging)
├── id (PK)
├── group_id (FK groups)
├── name
└── color_hex

TagAssignment ⭐ NEW
├── id (PK)
├── tag_id (FK tags)
├── entity_type (EXPENSE, CHORE, RECIPE, etc.)
├── entity_id
└── created_at
```

---

## 🔗 INTERFUNCTIONALITY MATRIX

### Critical Cross-Module Links:

1. **Expenses → Proposals**: Expense requests require votes
2. **Expenses → Pet Medical Records**: Vet bills auto-link
3. **Expenses → Maintenance Logs**: Repair costs tracked
4. **Chores → Items**: Auto-add cleaning supplies to shopping list
5. **Plants → Locations**: Sunlight compatibility warnings
6. **Plants → Pets**: Toxicity warnings if toxic plant + cat/dog
7. **Recipes → Shopping Lists**: One-click ingredient import
8. **Meal Plans → Recipes → Shopping Lists**: Full flow
9. **Home Assets → Maintenance Tasks → Items**: Auto-add required parts
10. **Recurring Expenses → Expenses**: Auto-generation
11. **Budgets → Expenses**: Real-time overspend alerts
12. **Inventory → Shopping Lists**: Auto-restock triggers
13. **Pet Schedules → Chores**: Pet care as daily chores
14. **Plant Schedules → Chores**: Watering as recurring tasks
15. **Achievements → All Modules**: Points from any activity
16. **Comments → Everything**: Discuss any entity
17. **Notifications → All Modules**: Alerts for any event
18. **Calendar Events → Pets/Assets**: Vet appointments, lease renewals
19. **Audit Log → Everything**: Track all changes
20. **Tags → Everything**: Cross-cutting organization
