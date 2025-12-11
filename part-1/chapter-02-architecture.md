# Chapter 2: Architecture Design

---

## 2.1 Monolith vs Microservices

Before writing any code, we need to make a fundamental decision about our application's structure.

### The Microservices Hype

You've probably heard that "microservices are the future" and "monoliths are dead." Let's examine this claim.

**Microservices architecture** means splitting your application into many small, independent services:

```
                    ┌──────────────┐
                    │   API Gateway │
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
    │ Auth Service│ │Content Svc  │ │Progress Svc │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
    ┌──────┴──────┐ ┌──────┴──────┐ ┌──────┴──────┐
    │  Users DB   │ │ Content DB  │ │ Progress DB │
    └─────────────┘ └─────────────┘ └─────────────┘
```

**Advantages:**
- Independent scaling
- Technology flexibility
- Team independence
- Fault isolation

**Disadvantages:**
- Network latency between services
- Distributed system complexity
- Operational overhead
- Debugging nightmares
- Higher infrastructure costs

### The Reality Check

Netflix, Amazon, and Google use microservices because they have:
- Thousands of developers
- Millions of users
- Billions in revenue to pay for infrastructure

For our educational platform, we have:
- 1-5 developers
- Hundreds to thousands of users
- A budget that prefers efficiency

**The truth**: Most applications don't need microservices. They add complexity that doesn't pay off until you're operating at massive scale.

---

## 2.2 The "Compact Monolith" Philosophy

We're going to build what I call a **"Compact Monolith"** — a single, well-structured application that's:

- **Simple to develop**: One codebase, one language
- **Simple to deploy**: One process to run
- **Simple to scale**: Optimize what matters
- **Easy to change**: Refactor to microservices later if needed

```
┌─────────────────────────────────────────────────┐
│              Compact Monolith                    │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │   Auth   │ │ Content  │ │ Progress │        │
│  │  Module  │ │  Module  │ │  Module  │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │            │            │               │
│  ┌────┴────────────┴────────────┴────┐         │
│  │         Shared Data Layer          │         │
│  └────────────────┬──────────────────┘         │
└───────────────────┼─────────────────────────────┘
                    │
         ┌──────────┴──────────┐
         │     SQLite DBs      │
         └─────────────────────┘
```

### Key Principles

1. **Modular by Design**: Clear separation of concerns
2. **Vertical Slices**: Each feature is self-contained
3. **Shared Infrastructure**: One database connection, one auth system
4. **No Premature Optimization**: Build simple, optimize when needed

---

## 2.3 Dual Database Strategy

One unique aspect of our architecture is using **two separate SQLite databases**.

### Why Two Databases?

Consider the nature of our data:

| Aspect | User Data | Content Data |
|--------|-----------|--------------|
| **Changes** | Frequently (every user action) | Rarely (admin updates) |
| **Size** | Grows with users | Fixed (course catalog) |
| **Backup** | Critical (user progress) | Less critical (can regenerate) |
| **Access** | Read/Write | Mostly Read |

### The Implementation

```
data/
├── users.db      # User-generated data
│   ├── users          # Account information
│   ├── sessions       # Login sessions
│   └── lesson_progress # Watch history, quiz scores
│
└── content.db    # Educational content
    ├── tracks         # Learning paths
    ├── series         # Course series
    ├── lessons        # Individual lessons
    └── videos         # Video segments
```

### Benefits

1. **Independent Backups**: Backup user data more frequently
2. **Easy Content Updates**: Replace content.db without affecting users
3. **Performance Isolation**: Heavy reads don't affect writes
4. **Development Simplicity**: Clear ownership of data

### Connection Setup

```typescript
// src/lib/server/db/index.ts

import { drizzle } from 'drizzle-orm/bun-sqlite';
import { Database } from 'bun:sqlite';

// User database (read-write)
const usersSqlite = new Database('data/users.db');
usersSqlite.exec('PRAGMA journal_mode = WAL');
usersSqlite.exec('PRAGMA foreign_keys = ON');

export const db = drizzle(usersSqlite);

// Content database (read-mostly)
const contentSqlite = new Database('data/content.db');
contentSqlite.exec('PRAGMA foreign_keys = ON');

export const contentDatabase = drizzle(contentSqlite);
```

---

## 2.4 Content vs User Data Separation

Let's define exactly what goes where.

### users.db — User-Generated Data

Everything that comes from user actions:

```sql
-- Who are our users?
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT DEFAULT 'user',  -- user, editor, admin
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Active login sessions
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,  -- UUID
    user_id INTEGER REFERENCES users(id),
    expires_at TEXT NOT NULL
);

-- Learning progress
CREATE TABLE lesson_progress (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    lesson_id TEXT NOT NULL,  -- References content.db
    watched_seconds INTEGER DEFAULT 0,
    video_completed INTEGER DEFAULT 0,
    quiz_passed INTEGER DEFAULT 0,
    quiz_score INTEGER DEFAULT 0
);
```

### content.db — Educational Content

All the learning material:

```sql
-- Learning tracks (e.g., "Islamic Creed", "Hadith Studies")
CREATE TABLE tracks (
    id TEXT PRIMARY KEY,  -- e.g., "aqeedah", "hadith"
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    "order" INTEGER DEFAULT 0
);

-- Series within tracks
CREATE TABLE series (
    id TEXT PRIMARY KEY,
    track_id TEXT REFERENCES tracks(id),
    title TEXT NOT NULL,
    instructor TEXT,
    is_locked INTEGER DEFAULT 0
);

-- Individual lessons
CREATE TABLE lessons (
    id TEXT PRIMARY KEY,
    track_id TEXT REFERENCES tracks(id),
    series_id TEXT REFERENCES series(id),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    is_published INTEGER DEFAULT 0
);

-- Video segments within lessons
CREATE TABLE videos (
    id TEXT PRIMARY KEY,
    lesson_id TEXT REFERENCES lessons(id),
    title TEXT,
    youtube_id TEXT,
    duration INTEGER,
    quiz TEXT  -- JSON array of questions
);
```

---

## 2.5 Designing for Scale

Even though we're building a monolith, we should design for growth.

### Scaling Strategies

**1. Vertical Scaling (Scale Up)**
- Add more CPU/RAM to the server
- Works until ~10,000 concurrent users
- Simple and effective

**2. Read Replicas**
```
┌─────────────┐
│  Primary DB │ ◄── Writes
└──────┬──────┘
       │ Replication
┌──────┴──────┐
│   Replica   │ ◄── Reads
└─────────────┘
```

**3. Edge Caching**
```
User → CDN → Server
         ↓
    Cached Content
```

**4. Eventually, Microservices**
If we grow to millions of users, we can extract services:
- Auth → Separate service
- Video processing → Separate service
- Search → ElasticSearch cluster

### Our Approach

We'll build with these principles:

1. **Stateless requests**: Any server can handle any request
2. **Database as source of truth**: No in-memory state
3. **Cacheable responses**: Proper HTTP headers
4. **Modular code**: Easy to extract later

---

## 2.6 Security Considerations from Day One

Security isn't an afterthought — it's baked into our architecture.

### Authentication Security

```
Password Flow:
User Input → bcrypt hash → Store hash
Login:      User Input → bcrypt verify → Session token
```

**Key decisions:**
- **bcrypt** for password hashing (not MD5, not SHA1)
- **Session tokens** stored in HttpOnly cookies
- **SameSite=Lax** to prevent CSRF
- **Secure flag** in production

### Authorization Layers

```
Request Flow:
1. hooks.server.ts  → Validate session
2. +page.server.ts  → Check role
3. Database query   → Filter by user
```

### Content Protection

```typescript
// Audit trail on every content table
{
    created_at: TEXT,       // When created
    updated_at: TEXT,       // When modified
    last_modified_by: TEXT, // Who modified
    is_locked: INTEGER      // Prevent changes
}
```

### Rate Limiting (Placeholder)

```typescript
// hooks.server.ts
if (url.pathname.startsWith('/api/auth')) {
    // TODO: Implement rate limiting
    // 5 requests per minute per IP
}
```

### SQL Injection Prevention

Drizzle ORM uses parameterized queries automatically:

```typescript
// Safe — Drizzle handles escaping
db.select()
  .from(users)
  .where(eq(users.email, userInput));

// NEVER do this
db.run(`SELECT * FROM users WHERE email = '${userInput}'`);
```

---

## Summary

In this chapter, we established our architectural foundation:

| Decision | Choice | Reason |
|----------|--------|--------|
| Architecture | Compact Monolith | Simplicity, low overhead |
| Database | Dual SQLite | Separation of concerns |
| Auth | Session-based | Simple, secure |
| Scaling | Start small, grow smart | Optimize when needed |
| Security | Defense in depth | Built-in from day one |

These decisions will guide every choice we make throughout the book. They're not set in stone — if your needs differ, adapt them. But for most educational platforms, this architecture will serve you well.

---

> **Next Chapter**: [Chapter 3: Setting Up the Development Environment](./chapter-03-setup.md)
