---
description: Create or update a task breakdown document from the tasks template, ensuring all tasks align with constitution quality standards
---

## User Input

```text
{{USER_INPUT}}
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are creating or updating a task breakdown based on `.specify/templates/tasks-template.md`. Your job is to decompose work into actionable tasks with clear constitution compliance checks.

Follow this execution flow:

1. **Context gathering:**
   - Review user input for task breakdown needs
   - Read related spec document to understand full scope
   - Read related plan if available for strategic context
   - Review current sprint/iteration scope if applicable

2. **Load governance:**
   - Read `.specify/memory/constitution.md`
   - Note task categories that correspond to principles
   - These will guide task classification and validation

3. **Decompose work:**
   - Break specification into implementable tasks
   - Ensure tasks are:
     - Atomic: completable in 1-2 days ideally
     - Clear: unambiguous description and acceptance criteria
     - Testable: can verify completion objectively
     - Prioritized: critical path identified
   
   - Categorize each task:
     - 🏗️ Development (code implementation)
     - 🧪 Testing (test creation/execution)
     - 🎨 Design/UX (UI/UX work)
     - ⚡ Performance (optimization)
     - 📝 Documentation (docs)
     - 🔍 Code Review (review work)
     - 🐛 Bug Fix (fixes)
     - ♿ Accessibility (a11y improvements)

4. **Fill the template:**
   - Load `.specify/templates/tasks-template.md`
   - Create a task entry for each work item
   
   **For each task include:**
   - Task name and category
   - Priority (Critical/High/Medium/Low)
   - Estimated effort
   - Assigned owner (if known)
   - Status (TODO/In Progress/In Review/Done)
   - Detailed description
   - Acceptance criteria checklist
   - Constitution compliance checklist:
     - Code Quality: standards adherence, complexity, review
     - Testing: coverage requirements, test inclusion
     - Performance: impact assessment, targets
     - UX: design system usage, accessibility (if UI work)
   - Dependencies on other tasks
   - Any blockers

5. **Identify critical path:**
   - Determine task dependencies
   - Identify sequence that must complete first
   - Flag critical path tasks clearly
   - Estimate overall timeline based on dependencies

6. **Validate completeness:**
   - All spec requirements mapped to tasks
   - No work items missing
   - Testing tasks included for all features
   - Code review tasks scheduled
   - Documentation tasks present
   - Performance validation tasks included
   - Accessibility tasks for UI work
   - Dependencies clearly stated
   - Constitution checks present on all implementation tasks

7. **Write the task document:**
   - Save to `.specify/tasks/[feature-name]-tasks.md` (use kebab-case)
   - Link back to related spec and plan

8. **Output summary:**
   - Confirm task document location
   - Provide task count by category
   - Highlight critical path and estimated timeline
   - Note any blockers or dependencies requiring attention
   - Suggest next steps (typically: assign tasks, begin sprint)
   - Provide suggested commit message

## Notes

- Task granularity should enable daily progress updates
- Overly large tasks should be broken down further
- Include time for code review, testing, and documentation—not just coding
- Constitution compliance checks ensure quality gates are clear
- Keep task status updated regularly
- Use task document as living artifact during sprint

