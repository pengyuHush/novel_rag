---
description: Create or update a detailed specification document from the spec template, ensuring all requirements align with constitution principles
---

## User Input

```text
{{USER_INPUT}}
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

You are creating or updating a detailed specification based on `.specify/templates/spec-template.md`. Your job is to gather detailed requirements, fill the template, and ensure comprehensive constitution compliance.

Follow this execution flow:

1. **Context gathering:**
   - Review user input for feature details
   - If a related plan exists, read it to understand strategic context
   - Identify related existing specs or dependencies
   - Review relevant codebase sections if feature is an enhancement

2. **Load governance:**
   - Read `.specify/memory/constitution.md`
   - Note all principles and their specific requirements
   - These will guide all sections of the spec

3. **Gather detailed requirements:**
   If not provided, ask for:
   - Functional requirements with priorities
   - Acceptance criteria for each requirement
   - User flows and interaction patterns
   - Technical constraints or preferences
   - Performance targets specific to this feature
   - Accessibility requirements beyond baseline
   - Security considerations

4. **Fill the template comprehensively:**
   - Load `.specify/templates/spec-template.md`
   - Replace all `[PLACEHOLDERS]` with concrete values
   
   **Constitution Alignment section:**
   - Explicitly state how each principle applies
   - Code Quality: standards, review process, complexity limits
   - Testing: specific coverage targets, test types, strategies
   - UX Consistency: design system components, patterns, accessibility
   - Performance: specific metrics for this feature
   
   **Requirements sections:**
   - Functional: detailed, prioritized, with clear acceptance criteria
   - Non-Functional: concrete targets from constitution, tailored to feature
   
   **User Experience section:**
   - Document all user flows step-by-step
   - Specify exact design system components
   - Define interaction patterns matching existing app
   - Include responsive design considerations
   - Detail accessibility implementation
   
   **Technical Design section:**
   - API contracts with performance targets
   - Data models with indexing strategy
   - State management approach
   - Error handling for client and server
   
   **Testing Requirements:**
   - Specific unit test coverage per module
   - Integration test scenarios
   - E2E test flows
   - Performance test criteria
   - Accessibility test checklist

5. **Validate completeness:**
   - No unexplained placeholder tokens
   - All constitution principles addressed with specifics
   - Every functional requirement has clear acceptance criteria
   - NFRs include measurable targets
   - User flows are complete and testable
   - Technical design is implementable
   - Testing requirements are comprehensive
   - Performance targets are specified
   - Accessibility is not overlooked

6. **Write the spec:**
   - Save to `.specify/specs/[feature-name]-spec.md` (use kebab-case)
   - Set version to 1.0.0 for new specs
   - If updating, increment version appropriately and document in Change Log

7. **Output summary:**
   - Confirm spec location and version
   - List any TODOs requiring further input
   - Highlight critical requirements or constraints
   - Suggest next steps (typically: break into tasks, begin implementation)
   - Provide suggested commit message

## Notes

- Specs should be detailed enough for implementation without ambiguity
- When in doubt, over-specify rather than under-specify
- Link to external diagrams, mockups, or references as needed
- Keep the spec up-to-date as implementation reveals new insights
- Version the spec semantically as requirements evolve

