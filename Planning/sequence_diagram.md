# Approval Sequence

```text
Journalist -> Django: Submit article
Django -> MariaDB: Save approved=False
Editor -> Django: Open review queue
Editor -> Django: Approve article
Django -> MariaDB: Set approved=True
Django -> Email backend: Send article to subscribers
Django -> /api/approved/: POST article_id using TokenAuthentication
API -> MariaDB: Create ApprovedArticleLog
API -> Django: 201 Created
Django -> Editor: Show approval result
```
