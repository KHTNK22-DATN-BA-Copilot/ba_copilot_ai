## BA Copilot Integrated Database Documentation

This document defines the single, shared PostgreSQL database used by both services:

- Backend service: `ba_copilot_backend` (auth, user profile, tokens, projects)
- AI service: `ba_copilot_ai` (SRS, diagrams, wireframes, conversations/messages)

Both services connect to the same PostgreSQL instance with a hierarchical data model:

1. Users manage multiple projects
2. Projects contain AI-generated artifacts (documents, wireframes, diagrams, conversations)

Data isolation is enforced through the project ownership hierarchy, where users can only access content within their own projects.

Notes on design alignment across repos:

- The Backend uses integer primary keys for `users.id` and `projects.id`.
- Projects act as the primary organizational unit for AI-generated content.
- AI tables reference `project_id` instead of directly referencing `user_id` for better organization.
- Foreign keys from AI tables to `projects` are recommended for data integrity.
- Users can CRUD projects, and all AI artifacts belong to specific projects.

Security and performance:

- Index all project-scoped entities on `(project_id, created_at)` for fast listings and pagination.
- Index projects on `(user_id, created_at)` for user project listings.
- Use Row Level Security (RLS) if multi-tenant isolation is required beyond application-level checks.
- Consider partitioning very large message tables by time.

---

## Logical ER Overview

- users (BE)
  - tokens (BE) many-to-one to users
  - projects (BE) many-to-one to users
    - documents (AI SRS) many-to-one to projects
    - wireframes (AI) many-to-one to projects
    - diagrams (AI) many-to-one to projects
    - conversations (AI) many-to-one to projects
      - messages (AI) many-to-one to conversations

---

## dbdiagram.io (DBML)

Copy-paste the following into https://dbdiagram.io to render the complete schema.

```dbml
Project BA_Copilot {
  database_type: 'PostgreSQL'
  note: 'Unified DB shared by Backend and AI services with project-based organization'
}

Table users {
  id               int [pk, increment]
  name             varchar(255) [not null]
  email            varchar(255) [not null, unique]
  passwordhash     varchar(255) [not null]
  email_verified   boolean [default: false]
  email_verification_token varchar(255)
  email_verification_expiration timestamptz
  reset_code       varchar(255)
  reset_code_expiration timestamptz
  created_at       timestamptz [default: `now()`]
  updated_at       timestamptz [default: `now()`]
}

Table tokens {
  id          int [pk, increment]
  token       varchar(255) [not null]
  expiry_date timestamptz [not null]
  user_id     int [not null, ref: > users.id]
  created_at  timestamptz [default: `now()`]
  updated_at  timestamptz [default: `now()`]
}

// Projects - new organizational layer
Table projects {
  id              int [pk, increment]
  user_id         int [not null, ref: > users.id]
  name            varchar(255) [not null]
  description     text
  status          varchar(32) [not null, default: 'active'] // active | archived | deleted
  settings        jsonb [default: '{}'] // project-specific AI settings
  created_at      timestamptz [default: `now()`]
  updated_at      timestamptz [default: `now()`]

  Note: 'Projects organize AI-generated content for users'

  Indexes {
    (user_id, created_at)
    (user_id, status)
    name
  }
}

// AI: SRS Documents
Table documents {
  document_id     uuid [pk, default: `gen_random_uuid()`]
  project_id      int [not null, ref: > projects.id]
  project_name    varchar(255) [not null] // denormalized for convenience
  content_markdown text [not null]
  status          varchar(32) [not null, default: 'generated'] // generated | draft | published
  document_metadata jsonb [default: '{}']
  version         int [not null, default: 1]
  created_at      timestamptz [default: `now()`]
  updated_at      timestamptz [default: `now()`]
  Note: 'AI SRS documents generated within projects'

  Indexes {
    (project_id, created_at)
    project_name
    status
  }
}

// AI: Wireframes
Table wireframes {
  wireframe_id  uuid [pk, default: `gen_random_uuid()`]
  project_id    int [not null, ref: > projects.id]
  title         varchar(255) [not null]
  description   text
  html_content  text [not null]
  css_content   text
  template_type varchar(64)
  metadata      jsonb [default: '{}']
  created_at    timestamptz [default: `now()`]
  updated_at    timestamptz [default: `now()`]

  Indexes {
    (project_id, created_at)
    title
    template_type
  }
}

// AI: Diagrams (sequence, architecture, usecase, flowchart)
Table diagrams {
  diagram_id    uuid [pk, default: `gen_random_uuid()`]
  project_id    int [not null, ref: > projects.id]
  diagram_type  varchar(32) [not null] // sequence | architecture | usecase | flowchart
  title         varchar(255) [not null]
  description   text
  mermaid_code  text [note: 'Mermaid or DSL code']
  image_url     varchar(1024)
  options       jsonb [default: '{}']
  created_at    timestamptz [default: `now()`]
  updated_at    timestamptz [default: `now()`]

  Indexes {
    (project_id, created_at)
    diagram_type
    title
  }
}

// AI: Conversations and Messages
Table conversations {
  conversation_id uuid [pk, default: `gen_random_uuid()`]
  project_id      int [not null, ref: > projects.id]
  title           varchar(255) [not null]
  metadata        jsonb [default: '{}']
  created_at      timestamptz [default: `now()`]
  updated_at      timestamptz [default: `now()`]

  Indexes {
    (project_id, created_at)
    title
  }
}

Table messages {
  message_id      uuid [pk, default: `gen_random_uuid()`]
  conversation_id uuid [not null, ref: > conversations.conversation_id]
  role            varchar(32) [not null] // user | assistant | system
  content         text [not null]
  metadata        jsonb [default: '{}']
  timestamp       timestamptz [default: `now()`]

  Indexes {
    conversation_id
    (conversation_id, timestamp)
    role
  }
}
```

---

## Deployment and Migrations

- Single Postgres instance, database name: `bacopilot_db`.
- Both services connect using the same `DATABASE_URL` (see docker-compose).
- Backend creates its tables at startup automatically: `users`, `tokens`
- **Important**: The `projects` table needs to be added to the backend service to complete the project-based architecture
- AI service applies Alembic migrations at container start (see docker-compose command override).

Connection string (inside containers):

- `postgresql://postgres:postgres123@postgres:5432/bacopilot_db`

### Implementation Steps

To complete the project-based architecture, the following needs to be implemented:

1. **Backend Service**: Add `projects` table and CRUD API endpoints

   - `POST /api/v1/projects` - Create project
   - `GET /api/v1/projects` - List user's projects
   - `GET /api/v1/projects/{id}` - Get project details
   - `PUT /api/v1/projects/{id}` - Update project
   - `DELETE /api/v1/projects/{id}` - Delete project

2. **AI Service**: Update all endpoints to require `project_id` parameter
   - Modify SRS, wireframes, diagrams, conversations endpoints
   - Add database models using SQLAlchemy/Alembic
   - Create migrations for AI tables

Optional hardening (production):

- Create a dedicated DB user per service with least privileges.
- Enable SSL/TLS for external connections.
- Set up automated backups and PITR.
