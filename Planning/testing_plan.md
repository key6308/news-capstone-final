# Testing Plan

## Automated tests

- Unauthenticated API request returns 401.
- Reader sees approved articles only.
- Reader subscribed endpoint returns publisher/journalist subscriptions and excludes unrelated articles.
- Non-reader is denied subscribed endpoint.
- Journalist can create an article.
- Reader cannot create an article.
- Journalist cannot modify another journalist's article.
- Editor can update/delete an article.
- Editor approval marks an article approved, emails subscribers, and logs to the internal API.
- Approval still completes if API logging fails.
- Journalist can create a newsletter.
- Reader cannot create a newsletter.
- Role groups are assigned.
- Custom-user login works.

## Manual/Postman checks

1. POST `/api/token/` with a demo username/password.
2. Use the returned token in Postman as `Authorization: Token <token>`.
3. GET `/api/articles/` as each authenticated role.
4. GET `/api/articles/subscribed/` as a reader with subscriptions.
5. POST `/api/articles/` as a journalist and confirm 201.
6. Repeat the POST as a reader and confirm 403.
7. PUT/DELETE an article as an editor and confirm success.
8. Visit the editor review page, approve a draft, and verify the email console output and `/api/approved/` log.
