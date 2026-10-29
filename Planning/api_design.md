# REST API Design

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/token/` | Public login endpoint | Get a DRF token |
| GET | `/api/articles/` | Authenticated | List approved articles |
| GET | `/api/articles/subscribed/` | Reader | List approved subscribed content |
| GET | `/api/articles/<id>/` | Authenticated | Retrieve one article |
| POST | `/api/articles/` | Journalist | Create an unapproved article |
| PUT/PATCH | `/api/articles/<id>/` | Editor or owning journalist | Update article |
| DELETE | `/api/articles/<id>/` | Editor or owning journalist | Delete article |
| GET | `/api/publishers/` | Authenticated | List publishers |
| GET | `/api/newsletters/` | Authenticated | List visible newsletters |
| POST | `/api/newsletters/` | Editor or journalist | Create newsletter |
| POST | `/api/approved/` | Editor | Log an approved article |

## Authentication

Django REST Framework Token Authentication is used. Clients send:

`Authorization: Token <token>`

Readers cannot POST/PUT/DELETE articles. Journalists can create and manage their own articles. Editors can manage articles and approve them through the web approval workflow.
