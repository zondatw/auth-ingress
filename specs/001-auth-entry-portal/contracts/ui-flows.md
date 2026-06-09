# UI Flow Contract: Auth Entry Portal

## Flow: Signed-Out User Enters a Protected Service

1. User opens `/services/{service_slug}`.
2. If no valid session exists, portal shows sign-in and preserves the requested
   service path.
3. User submits credentials.
4. If credentials are valid and the user is authorized, portal sends the user to
   the requested service route.
5. If credentials are valid but the user is not authorized, portal shows an
   access-denied page with a path back to the service list.
6. If credentials are invalid, portal shows a generic sign-in failure message and
   does not reveal which credential was wrong.

## Flow: Signed-In User Opens Portal Home

1. User opens `/`.
2. Portal validates the session.
3. Portal lists enabled services allowed by the user's groups.
4. If no services are available, portal shows an empty state with sign-out and
   support guidance.

## Flow: Signed-In User Enters a Service

1. User selects an allowed service from the portal list.
2. Portal validates that the session is active, the service is enabled, and an
   access rule allows the user.
3. Portal records a non-sensitive audit event.
4. Portal serves or launches the protected service route.

## Flow: Unauthorized Service Entry

1. User requests a service that is unknown, disabled, or not allowed.
2. Portal does not expose the protected service.
3. Portal records a non-sensitive denied-access audit event.
4. Portal shows a clear unavailable or unauthorized message.

## Flow: Administrator Manages Service Entries

1. Admin opens `/admin/services`.
2. Portal verifies the admin permission.
3. Admin creates, updates, or disables a service entry.
4. Portal validates slug, display name, destination, enabled state, and group
   access rules.
5. Portal saves the change and records a non-sensitive audit event.

## Flow: Sign Out and Browser History

1. Signed-in user submits sign-out.
2. Portal revokes the session and records sign-out.
3. User navigates back with browser history.
4. Portal revalidates the session before any protected decision and sends the
   user to sign in instead of restoring access.
