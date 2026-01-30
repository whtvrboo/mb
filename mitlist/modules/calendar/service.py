"""Calendar module service layer. PRIVATE - other modules import from interface.py."""

from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_calendar_feed(
    db: AsyncSession,
    group_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict[str, Any]]:
    """
    Get a unified calendar feed for a group.

    Aggregates:
    - Bills/recurring expenses due dates
    - Chore deadlines
    - Meal plans
    - Pet vaccine schedules
    - Member birthdays
    - Lease expiry dates
    """
    events: list[dict[str, Any]] = []

    # Default date range: current month
    if start_date is None:
        today = date.today()
        start_date = today.replace(day=1)
    if end_date is None:
        # End of month + next month for lookahead
        next_month = start_date.replace(day=28) + timedelta(days=4)
        end_date = next_month.replace(day=1) + timedelta(days=30)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())

    # 1. Bills / Recurring Expenses
    try:
        from mitlist.modules.finance.models import RecurringExpense
        result = await db.execute(
            select(RecurringExpense).where(
                RecurringExpense.group_id == group_id,
                RecurringExpense.is_active.is_(True),
            )
        )
        recurring_expenses = result.scalars().all()
        for expense in recurring_expenses:
            if expense.next_due_date and start_date <= expense.next_due_date <= end_date:
                events.append({
                    "id": f"bill_{expense.id}",
                    "type": "BILL",
                    "title": expense.name,
                    "date": expense.next_due_date.isoformat(),
                    "amount": float(expense.amount) if expense.amount else None,
                    "entity_id": expense.id,
                    "entity_type": "recurring_expense",
                })
    except Exception:
        pass  # Module may not exist or table may not exist

    # 2. Chore Deadlines
    try:
        from mitlist.modules.chores.models import Chore, ChoreAssignment
        result = await db.execute(
            select(ChoreAssignment)
            .join(Chore, ChoreAssignment.chore_id == Chore.id)
            .where(
                Chore.group_id == group_id,
                ChoreAssignment.status == "PENDING",
                ChoreAssignment.due_date >= start_dt,
                ChoreAssignment.due_date <= end_dt,
            )
        )
        assignments = result.scalars().all()
        for assignment in assignments:
            # Get chore name
            chore_result = await db.execute(
                select(Chore).where(Chore.id == assignment.chore_id)
            )
            chore = chore_result.scalar_one_or_none()
            events.append({
                "id": f"chore_{assignment.id}",
                "type": "CHORE",
                "title": chore.name if chore else "Chore",
                "date": assignment.due_date.isoformat() if assignment.due_date else None,
                "assigned_to_id": assignment.assigned_to_id,
                "entity_id": assignment.id,
                "entity_type": "chore_assignment",
            })
    except Exception:
        pass

    # 3. Meal Plans
    try:
        from mitlist.modules.recipes.models import MealPlan, Recipe
        result = await db.execute(
            select(MealPlan).where(
                MealPlan.group_id == group_id,
                MealPlan.plan_date >= start_date,
                MealPlan.plan_date <= end_date,
            )
        )
        meal_plans = result.scalars().all()
        for mp in meal_plans:
            recipe_title = None
            if mp.recipe_id:
                recipe_result = await db.execute(
                    select(Recipe).where(Recipe.id == mp.recipe_id)
                )
                recipe = recipe_result.scalar_one_or_none()
                recipe_title = recipe.title if recipe else None
            events.append({
                "id": f"meal_{mp.id}",
                "type": "MEAL_PLAN",
                "title": recipe_title or mp.notes or f"{mp.meal_type} meal",
                "date": mp.plan_date.isoformat(),
                "meal_type": mp.meal_type,
                "assigned_cook_id": mp.assigned_cook_id,
                "entity_id": mp.id,
                "entity_type": "meal_plan",
            })
    except Exception:
        pass

    # 4. Pet Vaccine Schedules
    try:
        from mitlist.modules.pets.models import Pet, VetVisit
        # Get pets for the group
        pets_result = await db.execute(
            select(Pet).where(Pet.group_id == group_id)
        )
        pets = {p.id: p for p in pets_result.scalars().all()}

        # Get upcoming vet visits
        visits_result = await db.execute(
            select(VetVisit).where(
                VetVisit.pet_id.in_(list(pets.keys())),
                VetVisit.scheduled_date >= start_date,
                VetVisit.scheduled_date <= end_date,
            )
        )
        visits = visits_result.scalars().all()
        for visit in visits:
            pet = pets.get(visit.pet_id)
            events.append({
                "id": f"vet_{visit.id}",
                "type": "PET_VET_VISIT",
                "title": f"{pet.name if pet else 'Pet'}: {visit.visit_type}",
                "date": visit.scheduled_date.isoformat(),
                "pet_id": visit.pet_id,
                "entity_id": visit.id,
                "entity_type": "vet_visit",
            })
    except Exception:
        pass

    # 5. Lease Expiry
    try:
        from mitlist.modules.auth.models import Group
        result = await db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        if group and group.lease_end_date:
            lease_end = group.lease_end_date
            if isinstance(lease_end, datetime):
                lease_end = lease_end.date()
            if start_date <= lease_end <= end_date:
                events.append({
                    "id": f"lease_{group_id}",
                    "type": "LEASE_EXPIRY",
                    "title": "Lease Expiry",
                    "date": lease_end.isoformat(),
                    "entity_id": group_id,
                    "entity_type": "group",
                })
    except Exception:
        pass

    # 6. Member birthdays: skipped (would require birthday on User model)

    # Sort events by date
    events.sort(key=lambda e: e.get("date", ""))

    return events
