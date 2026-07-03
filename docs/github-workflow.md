# GitHub Workflow

This project uses GitHub Issues, GitHub Projects, and pull requests as a lightweight alternative to Jira.

## Project Board

Recommended columns:

```text
Backlog
Todo
In Progress
Review
Done
```

## Column Meaning

### Backlog

Ideas, unconfirmed bugs, future improvements, or tickets needing more details.

### Todo

Tickets ready to be implemented. A ready ticket should include context, objective, expected behavior, and acceptance criteria.

### In Progress

Tickets currently being worked on. Move a ticket here when a branch is created or implementation starts.

### Review

Tickets with a pull request opened and ready for human validation.

### Done

Tickets completed, validated, and merged.

## Recommended Labels

```text
bug
feature
tech-debt
urgent
backend
frontend
mobile
blocked
documentation
testing
refactor
security
```

## Issue Format

Each issue should include:

```md
## Context

Describe the problem or need.

## Objective

Explain the expected result.

## Current Behavior

Describe what currently happens.

## Expected Behavior

Describe what should happen.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Constraints

- Keep the solution simple.
- Respect the existing architecture.
- Avoid changes outside the ticket scope.
- Add or adapt tests when necessary.

## Technical Notes

Mention likely files, modules, endpoints, components, or services.
```

## Branch Naming

Use:

```text
type/issue-number-short-description
```

Accepted types:

```text
bug
feature
refactor
docs
test
security
chore
```

## Pull Request Format

Every pull request should contain:

```md
## Summary

Briefly describe what was done.

## Linked Ticket

Closes #ISSUE_NUMBER

## Main Changes

- Change 1
- Change 2
- Change 3

## Tests

- [ ] Unit tests added or updated
- [ ] Integration tests added or updated when necessary
- [ ] Manual test completed

## Risks

Describe possible risks or write: No major risk identified.

## Notes

Add useful review notes.
```
