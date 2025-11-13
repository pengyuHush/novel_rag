---
description: Create or update a project plan document from the plan template, ensuring alignment with constitution principles
---

## User Input

```text
{{USER_INPUT}}
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are creating or updating a project plan based on `.specify/templates/plan-template.md`. Your job is to gather requirements, fill the template, and ensure constitution compliance.

Follow this execution flow:

1. **Understand the scope:**
   - Review user input to understand the feature/project being planned
   - Identify the primary goals, stakeholders, and constraints
   - Determine if this is a new plan or an update to an existing one

2. **Load the constitution:**
   - Read `.specify/memory/constitution.md`
   - Note the current version and all principles
   - Use these principles to guide the planning process

3. **Gather information:**
   If not provided in user input, ask for:
   - Feature/project name
   - Owner/lead
   - Primary goals and success metrics
   - Scope (in/out)
   - Technology stack preferences
   - Timeline constraints

4. **Fill the template:**
   - Load `.specify/templates/plan-template.md`
   - Replace all `[PLACEHOLDERS]` with concrete values
   - Complete the Constitution Compliance Check section with specific details
   - Define clear, measurable success metrics including performance baselines
   - Outline architecture following code quality and performance principles
   - Define comprehensive testing strategy aligned with testing standards
   - Ensure UX design considers consistency and accessibility requirements

5. **Validate completeness:**
   - No placeholder tokens remaining (or explicitly marked as TODO with rationale)
   - All constitution principles addressed in compliance check
   - Success metrics are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
   - Testing strategy meets coverage and quality standards
   - Performance requirements specified per constitution targets
   - Timeline is realistic and phased appropriately

6. **Write the plan:**
   - Save to `.specify/plans/[feature-name]-plan.md` (use kebab-case for filename)
   - If updating existing plan, preserve version history in Notes & Updates section

7. **Output summary:**
   - Confirm plan location
   - Highlight any areas needing further input (TODOs)
   - Suggest next steps (typically: create detailed spec, break into tasks)
   - Provide suggested commit message

## Notes

- Plans should be strategic and high-level, not overly detailed
- Details belong in spec documents
- Always cross-reference related documents
- Update plan status as work progresses

