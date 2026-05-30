# REQUESTS.md

## Active

### R-007 — Link entries to recurring tasks to prevent recreation after moves
Priority: high  
Status: proposed

Why:
Recurring task entries are still recreated when the originally generated entry is moved to another day.
The current logic appears to rely too much on date-based matching and cannot reliably detect that an existing entry already belongs to the recurring task for the current week.

Change:
Enhance the data model so an `Entry` can be explicitly linked to its originating recurring task.
Use this relation in the weekly recurring-task logic to check whether an entry for that recurring task already exists in the current week, even if it was moved to another day.

Goal:
Prevent duplicate recreation, simplify recurring-task resolution, and make the logic more explicit and maintainable.

Suggested model direction:
- Add a nullable foreign key on `Entry` that links to the originating recurring task template or recurring task instance.
- Define one clear source of truth for “this weekly recurring task already has an entry”.
- Refactor generation/materialization logic to use the relation instead of only comparing dates or titles.

Acceptance criteria:
- An entry created from a recurring task keeps a persistent relation to that recurring task.
- If the entry is moved to another day within the same week, the system does not create a second entry for the same recurring task.
- Weekly recurring-task generation checks relation-based existence first.
- The recurring-task logic becomes simpler and more explicit than the current date-matching approach.
- Existing entries can be migrated safely or handled with a documented fallback strategy.
- Behavior is covered by tests for:
  - initial creation
  - moved entry within the same week
  - edited entry
  - no duplicate recreation
  - next-week generation still works correctly

Implementation notes:
- Prefer a simple relational design over heuristic matching.
- Keep the foreign key nullable for normal non-recurring entries.
- Document whether the relation points to `RecurringTaskTemplate` or to a materialized weekly recurring-task instance.
- If a schema migration is required, keep it minimal and explicit.