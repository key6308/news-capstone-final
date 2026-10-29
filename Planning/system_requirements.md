# System Requirements

## Functional requirements

1. Readers can register, log in, view approved articles and newsletters, and subscribe to publishers and journalists.
2. Journalists can create, view, update, and delete their own articles and newsletters.
3. Editors can review, approve, update, and delete articles and create/update/delete newsletters.
4. An article belongs to exactly one owner type: an independent journalist or a publisher.
5. Approved articles are emailed to the relevant subscribers.
6. Approval also sends a POST request to the project's `/api/approved/` endpoint.
7. The REST API uses token authentication and role-based authorization.
8. Automated tests verify successful and rejected requests and subscription filtering.

## Non-functional requirements

- Readable, modular Python following PEP 8 conventions.
- MariaDB relational database with normalized entities.
- Defensive validation and exception handling.
- Authentication and least-privilege role permissions.
- Sensitive configuration is stored in environment variables and `.env` is ignored by Git.
- API responses use JSON and HTTP status codes.
