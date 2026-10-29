# Normalized Data Model

- **User** stores account and role information. Reader subscriptions are many-to-many relationships to Publisher and Journalist users.
- **Publisher** stores publication data and has many-to-many relationships with its editors and journalists.
- **Article** stores one story and has exactly one owner: `author` or `publisher`.
- **Newsletter** stores a curated collection and connects to many approved articles through a many-to-many table.
- **ApprovedArticleLog** stores the internal API publication log for each approved article.

The design avoids repeating publisher or user details inside each article and uses relationships for reusable entities.
