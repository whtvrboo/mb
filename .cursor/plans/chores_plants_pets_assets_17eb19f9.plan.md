---
name: Chores Plants Pets Assets
overview: Complete chores module gaps (dependencies, templates, stats) and implement plants, pets, and assets modules from stub to full CRUD with care logging and schedules.
todos:
  - id: chores-deps
    content: Add chore dependencies service + endpoints
    status: pending
  - id: chores-templates
    content: Add chore templates service + endpoints
    status: pending
  - id: chores-stats
    content: Add statistics/leaderboard service + endpoints
    status: pending
  - id: chores-start-rate
    content: Add start and rate assignment endpoints
    status: pending
  - id: plants-full
    content: Implement full plants module (species, plants, logs, schedules)
    status: pending
  - id: pets-full
    content: Implement full pets module (pets, medical, logs, schedules)
    status: pending
  - id: assets-full
    content: Implement full assets module (assets, maintenance, insurance)
    status: pending
isProject: false
---

# Chores, Plants, Pets, Assets Implementation

## Chores Module - Gap Completion

**Current state**: 10 endpoints implemented, service layer complete

**Missing features** (schemas exist, no implementation):

### 1. Chore Dependencies

```python
async def add_dependency(db, chore_id, depends_on_chore_id, dependency_type) -> ChoreDependency
async def remove_dependency(db, dependency_id) -> None
async def get_dependencies(db, chore_id) -> list[ChoreDependency]
async def check_dependencies_met(db, assignment_id) -> bool
```

**Endpoints to add:**

- `GET /chores/{id}/dependencies`
- `POST /chores/{id}/dependencies`
- `DELETE /chores/dependencies/{id}`

### 2. Chore Templates (Library)

```python
async def list_templates(db, include_public=True) -> list[ChoreTemplate]
async def create_template(db, name, ..., is_public=False) -> ChoreTemplate
async def create_chore_from_template(db, template_id, group_id, overrides: dict) -> Chore
```

**Endpoints to add:**

- `GET /chores/templates`
- `POST /chores/templates`
- `POST /chores/templates/{id}/instantiate`

### 3. Statistics and Leaderboard

```python
async def get_group_stats(db, group_id) -> ChoreStatisticsResponse
async def get_user_stats(db, group_id, user_id) -> UserChoreStatsResponse
async def get_leaderboard(db, group_id, period="monthly") -> ChoreLeaderboardResponse
```

**Endpoints to add:**

- `GET /chores/stats`
- `GET /chores/stats/me`
- `GET /chores/leaderboard`

### 4. Assignment Start and Rating

```python
async def start_assignment(db, assignment_id, user_id) -> ChoreAssignment
async def rate_assignment(db, assignment_id, rated_by_id, quality_rating) -> ChoreAssignment
```

**Endpoints to add:**

- `PATCH /chores/assignments/{id}/start`
- `POST /chores/assignments/{id}/rate`

---

## Plants Module - Full Implementation

**Models exist**: `PlantSpecies`, `Plant`, `PlantLog`, `PlantSchedule`

**All 7 endpoints are stubs**

### Service Functions

```python
# Species (reference data)
async def list_species(db, search=None) -> list[PlantSpecies]
async def get_species_by_id(db, species_id) -> PlantSpecies | None

# Plants
async def list_plants(db, group_id) -> list[Plant]
async def get_plant_by_id(db, plant_id) -> Plant | None
async def create_plant(db, group_id, species_id, nickname, location, ...) -> Plant
async def update_plant(db, plant_id, **updates) -> Plant
async def mark_plant_dead(db, plant_id, reason) -> Plant

# Care Logs
async def list_plant_logs(db, plant_id, limit=50) -> list[PlantLog]
async def create_plant_log(db, plant_id, user_id, action_type, notes) -> PlantLog

# Schedules
async def list_plant_schedules(db, plant_id) -> list[PlantSchedule]
async def create_schedule(db, plant_id, action_type, frequency_days) -> PlantSchedule
async def mark_schedule_done(db, schedule_id, user_id) -> PlantSchedule
async def get_overdue_schedules(db, group_id) -> list[PlantSchedule]
```

### API Endpoints

| Method  | Path                          | Description            |
| ------- | ----------------------------- | ---------------------- |
| `GET`   | `/plants/species`             | List plant species     |
| `GET`   | `/plants`                     | List group plants      |
| `POST`  | `/plants`                     | Create plant           |
| `GET`   | `/plants/{id}`                | Get plant with species |
| `PATCH` | `/plants/{id}`                | Update plant           |
| `POST`  | `/plants/{id}/mark-dead`      | Mark plant deceased    |
| `GET`   | `/plants/{id}/logs`           | Get care logs          |
| `POST`  | `/plants/{id}/logs`           | Log care action        |
| `GET`   | `/plants/{id}/schedules`      | Get care schedules     |
| `POST`  | `/plants/{id}/schedules`      | Create schedule        |
| `PATCH` | `/plants/schedules/{id}/done` | Mark schedule done     |

---

## Pets Module - Full Implementation

**Models exist**: `Pet`, `PetMedicalRecord`, `PetLog`, `PetSchedule`

**All 7 endpoints are stubs**

### Service Functions

```python
# Pets
async def list_pets(db, group_id) -> list[Pet]
async def get_pet_by_id(db, pet_id) -> Pet | None
async def create_pet(db, group_id, name, species, ...) -> Pet
async def update_pet(db, pet_id, **updates) -> Pet
async def mark_pet_deceased(db, pet_id, date, notes) -> Pet

# Medical Records
async def list_medical_records(db, pet_id) -> list[PetMedicalRecord]
async def create_medical_record(db, pet_id, record_type, performed_at, ...) -> PetMedicalRecord
async def get_expiring_vaccines(db, group_id, days_ahead=30) -> list[PetMedicalRecord]

# Care Logs
async def list_pet_logs(db, pet_id, limit=50) -> list[PetLog]
async def create_pet_log(db, pet_id, user_id, activity_type, notes) -> PetLog

# Schedules
async def list_pet_schedules(db, pet_id) -> list[PetSchedule]
async def create_pet_schedule(db, pet_id, activity_type, frequency) -> PetSchedule
async def mark_schedule_done(db, schedule_id, user_id) -> PetSchedule
```

### API Endpoints

| Method  | Path                       | Description           |
| ------- | -------------------------- | --------------------- |
| `GET`   | `/pets`                    | List group pets       |
| `POST`  | `/pets`                    | Create pet            |
| `GET`   | `/pets/{id}`               | Get pet               |
| `PATCH` | `/pets/{id}`               | Update pet            |
| `POST`  | `/pets/{id}/mark-deceased` | Mark pet deceased     |
| `GET`   | `/pets/{id}/medical`       | Get medical records   |
| `POST`  | `/pets/{id}/medical`       | Create medical record |
| `GET`   | `/pets/{id}/logs`          | Get care logs         |
| `POST`  | `/pets/{id}/logs`          | Log care action       |
| `GET`   | `/pets/{id}/schedules`     | Get schedules         |
| `POST`  | `/pets/{id}/schedules`     | Create schedule       |
| `GET`   | `/pets/vaccines/expiring`  | Get expiring vaccines |

---

## Assets Module - Full Implementation

**Models exist**: `HomeAsset`, `MaintenanceTask`, `MaintenanceLog`, `AssetInsurance`

**All 4 endpoints are stubs**

### Service Functions

```python
# Assets
async def list_assets(db, group_id, category=None) -> list[HomeAsset]
async def get_asset_by_id(db, asset_id) -> HomeAsset | None
async def create_asset(db, group_id, name, category, ...) -> HomeAsset
async def update_asset(db, asset_id, **updates) -> HomeAsset
async def dispose_asset(db, asset_id, disposal_method, notes) -> HomeAsset

# Maintenance Tasks
async def list_maintenance_tasks(db, asset_id) -> list[MaintenanceTask]
async def create_maintenance_task(db, asset_id, name, frequency, ...) -> MaintenanceTask
async def get_overdue_maintenance(db, group_id) -> list[MaintenanceTask]

# Maintenance Logs
async def create_maintenance_log(db, task_id, user_id, completed_at, ...) -> MaintenanceLog
    # Also updates task.next_due_date

# Insurance
async def list_insurance(db, group_id) -> list[AssetInsurance]
async def create_insurance(db, group_id, type, provider, ...) -> AssetInsurance
async def get_expiring_insurance(db, group_id, days_ahead=30) -> list[AssetInsurance]
```

### API Endpoints

| Method  | Path                                     | Description             |
| ------- | ---------------------------------------- | ----------------------- |
| `GET`   | `/assets`                                | List group assets       |
| `POST`  | `/assets`                                | Create asset            |
| `GET`   | `/assets/{id}`                           | Get asset               |
| `PATCH` | `/assets/{id}`                           | Update asset            |
| `POST`  | `/assets/{id}/dispose`                   | Dispose asset           |
| `GET`   | `/assets/{id}/maintenance`               | Get maintenance tasks   |
| `POST`  | `/assets/{id}/maintenance`               | Create maintenance task |
| `POST`  | `/assets/{id}/maintenance/{task_id}/log` | Log maintenance done    |
| `GET`   | `/assets/maintenance/overdue`            | Get overdue maintenance |
| `GET`   | `/assets/insurance`                      | List insurance policies |
| `POST`  | `/assets/insurance`                      | Create insurance policy |
| `GET`   | `/assets/insurance/expiring`             | Get expiring insurance  |

---

## Files to Modify

**Chores:**

- `[mitlist/modules/chores/service.py](mitlist/modules/chores/service.py)`
- `[mitlist/modules/chores/api.py](mitlist/modules/chores/api.py)`

**Plants:**

- `[mitlist/modules/plants/service.py](mitlist/modules/plants/service.py)`
- `[mitlist/modules/plants/api.py](mitlist/modules/plants/api.py)`

**Pets:**

- `[mitlist/modules/pets/service.py](mitlist/modules/pets/service.py)`
- `[mitlist/modules/pets/api.py](mitlist/modules/pets/api.py)`

**Assets:**

- `[mitlist/modules/assets/service.py](mitlist/modules/assets/service.py)`
- `[mitlist/modules/assets/api.py](mitlist/modules/assets/api.py)`
