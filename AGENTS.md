# nomi CLI repository

## Implementation rules

- Follow the command pattern already used in this repository.
- Do not add a production dependency for this task.
- Add or update a regression test for every behaviour change.
- Treat an empty name as invalid input and preserve the existing exit-code convetions.

## Verification

- Run the repository's documented test command.
- In the final response, report the test result and one manual example of the new command.

## Agent skills

### Issue tracker

Issues and specs are tracked in this repository's GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Uses the default five canonical triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

Uses a single-context layout. See `docs/agents/domain.md`.
