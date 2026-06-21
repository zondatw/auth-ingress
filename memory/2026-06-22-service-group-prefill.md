# Debug Report: Existing service groups were blank

- **Date**: 2026-06-22
- **Symptom**: Existing services displayed an empty groups field on the service management page even though access rules existed.
- **Root cause**: The admin page queried services and groups independently but did not load the group assignments for each service. The edit template rendered `group_names` without a value binding. Persistence was intact.
- **Fix**: Query `AccessRule` joined to `Group`, build a comma-separated group-name value per service, and bind it to the edit input.
- **Evidence**: The seeded `demo → staff` mapping was present in SQLite. The new regression test failed before the change and passed afterward.
- **Regression test**: `tests/integration/test_admin_services.py::test_existing_service_form_prefills_assigned_groups`
- **Full validation**: 38 tests passed; one upstream Starlette TestClient deprecation warning remains.
- **Status**: DONE
