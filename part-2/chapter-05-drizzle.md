# Chapter 5: Drizzle ORM Setup

---

## 5.1 Introduction to Drizzle

Drizzle is a modern TypeScript ORM that's lightweight, type-safe, and perfect for SQLite.

### Why Drizzle?

| Feature | Drizzle | Prisma | TypeORM |
|---------|---------|--------|---------|
| Bundle size | ~50KB | ~2MB | ~500KB |
| TypeScript | Native | Generated | Decorators |
| SQLite support | Excellent | Good | Basic |
| Learning curve | Low | Medium | High |
| Raw SQL access | Easy | Harder | Medium |

### Core Philosophy

Drizzle follows "SQL-like" syntax:

```typescript
// Drizzle - feels like SQL
db.select()
  .from(users)
  .where(eq(users.email, email))
  .limit(1);

// Actual SQL it generates
// SELECT * FROM users WHERE email = ? LIMIT 1
```

### Installation

```bash
bun add drizzle-orm
bun add -d drizzle-kit
```

---

## 5.2 Schema Definition

Let's define our schemas using Drizzle's declarative syntax.

### users.db Schema

Create `src/lib/server/db/schema.ts`:

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

// ============================================
// USERS DATABASE SCHEMA (users.db)
// ============================================

// Users table
export const users = sqliteTable('users', {
    id: integer('id').primaryKey({ autoIncrement: true }),
    email: text('email').notNull().unique(),
    passwordHash: text('password_hash').notNull(),
    name: text('name').notNull(),
    role: text('role').default('user').notNull(), // user | editor | admin
    avatar: text('avatar'),
    isActive: integer('is_active', { mode: 'boolean' }).default(true).notNull(),
    createdAt: text('created_at').default('CURRENT_TIMESTAMP').notNull(),
    updatedAt: text('updated_at'),
});

// Sessions table
export const sessions = sqliteTable('sessions', {
    id: text('id').primaryKey(), // UUID
    userId: integer('user_id')
        .notNull()
        .references(() => users.id, { onDelete: 'cascade' }),
    expiresAt: text('expires_at').notNull(),
    createdAt: text('created_at').default('CURRENT_TIMESTAMP').notNull(),
});

// Lesson Progress table
export const lessonProgress = sqliteTable('lesson_progress', {
    id: integer('id').primaryKey({ autoIncrement: true }),
    userId: integer('user_id')
        .notNull()
        .references(() => users.id, { onDelete: 'cascade' }),
    lessonId: text('lesson_id').notNull(),
    watchedSeconds: integer('watched_seconds').default(0).notNull(),
    videoCompleted: integer('video_completed', { mode: 'boolean' }).default(false).notNull(),
    quizPassed: integer('quiz_passed', { mode: 'boolean' }).default(false).notNull(),
    quizScore: integer('quiz_score').default(0),
    completedAt: text('completed_at'),
    updatedAt: text('updated_at').default('CURRENT_TIMESTAMP').notNull(),
});

// Type exports
export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Session = typeof sessions.$inferSelect;
export type LessonProgress = typeof lessonProgress.$inferSelect;
```

### content.db Schema

Create `src/lib/server/db/schema-content.ts`:

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

// ============================================
// CONTENT DATABASE SCHEMA (content.db)
// ============================================

// Tracks (Learning Paths)
export const tracks = sqliteTable('tracks', {
    id: text('id').primaryKey(),
    title: text('title').notNull(),
    description: text('description'),
    icon: text('icon'),
    order: integer('order').default(0).notNull(),
});

// Series (Course Collections)
export const series = sqliteTable('series', {
    id: text('id').primaryKey(),
    trackId: text('track_id').references(() => tracks.id),
    title: text('title').notNull(),
    description: text('description'),
    instructor: text('instructor'),
    thumbnailUrl: text('thumbnail_url'),
    order: integer('order').default(0).notNull(),
    // Audit fields
    createdAt: text('created_at').default('CURRENT_TIMESTAMP'),
    updatedAt: text('updated_at'),
    lastModifiedBy: text('last_modified_by').default('script'),
    isLocked: integer('is_locked', { mode: 'boolean' }).default(false),
});

// Lessons
export const lessons = sqliteTable('lessons', {
    id: text('id').primaryKey(),
    trackId: text('track_id').references(() => tracks.id),
    seriesId: text('series_id').references(() => series.id),
    title: text('title').notNull(),
    slug: text('slug').notNull().unique(),
    description: text('description'),
    instructor: text('instructor'),
    thumbnailUrl: text('thumbnail_url'),
    pdfUrl: text('pdf_url'),
    order: integer('order').default(0).notNull(),
    isPublished: integer('is_published', { mode: 'boolean' }).default(false).notNull(),
    // Audit fields
    createdAt: text('created_at').default('CURRENT_TIMESTAMP'),
    updatedAt: text('updated_at'),
    lastModifiedBy: text('last_modified_by').default('script'),
    isLocked: integer('is_locked', { mode: 'boolean' }).default(false),
});

// Videos
export const videos = sqliteTable('videos', {
    id: text('id').primaryKey(),
    lessonId: text('lesson_id')
        .notNull()
        .references(() => lessons.id, { onDelete: 'cascade' }),
    title: text('title'),
    youtubeId: text('youtube_id'),
    downloadUrl: text('download_url'),
    duration: integer('duration'),
    summary: text('summary'),
    rawTranscript: text('raw_transcript'),
    formattedTranscript: text('formatted_transcript'),
    quiz: text('quiz'), // JSON
    order: integer('order').default(0).notNull(),
    // Audit fields
    createdAt: text('created_at').default('CURRENT_TIMESTAMP'),
    updatedAt: text('updated_at'),
    lastModifiedBy: text('last_modified_by').default('script'),
    isLocked: integer('is_locked', { mode: 'boolean' }).default(false),
});

// Type exports
export type Track = typeof tracks.$inferSelect;
export type Series = typeof series.$inferSelect;
export type Lesson = typeof lessons.$inferSelect;
export type Video = typeof videos.$inferSelect;
```

---

## 5.3 Type-Safe Queries

Drizzle provides complete type safety for all queries.

### Basic Select

```typescript
import { db } from '$lib/server/db';
import { users } from '$lib/server/db/schema';
import { eq } from 'drizzle-orm';

// Get user by email
const user = db
    .select()
    .from(users)
    .where(eq(users.email, 'test@example.com'))
    .get();

// TypeScript knows: user is User | undefined
```

### Select Specific Columns

```typescript
// Only get what you need
const userNames = db
    .select({
        id: users.id,
        name: users.name,
    })
    .from(users)
    .all();

// Type: { id: number; name: string }[]
```

### Insert

```typescript
// Insert returns the inserted row
const newUser = db
    .insert(users)
    .values({
        email: 'new@example.com',
        passwordHash: hashedPassword,
        name: 'New User',
    })
    .returning()
    .get();

// newUser is User
```

### Update

```typescript
// Update with conditions
db.update(users)
    .set({
        name: 'Updated Name',
        updatedAt: new Date().toISOString(),
    })
    .where(eq(users.id, userId))
    .run();
```

### Delete

```typescript
// Delete with conditions
db.delete(sessions)
    .where(eq(sessions.id, sessionId))
    .run();
```

---

## 5.4 Migrations Strategy

For our project, we use a simpler approach than traditional migrations.

### Why Not Traditional Migrations?

Traditional migration systems (like Prisma Migrate) are great for teams and complex deployments. But for our case:

- Single developer or small team
- SQLite (easy to backup/restore)
- Content database that can be regenerated

### Our Approach: Setup Scripts

**Create tables script** (`scripts/setup-db.ts`):

```typescript
import { Database } from 'bun:sqlite';
import { resolve } from 'path';

const dataDir = resolve(import.meta.dir, '../data');

console.log('🗄️  Creating users.db...');

const db = new Database(resolve(dataDir, 'users.db'), { create: true });

db.exec('PRAGMA journal_mode = WAL');
db.exec('PRAGMA foreign_keys = ON');

db.exec(`
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'user' NOT NULL,
        avatar TEXT,
        is_active INTEGER DEFAULT 1 NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TEXT
    );

    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        expires_at TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
    );

    CREATE TABLE IF NOT EXISTS lesson_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        lesson_id TEXT NOT NULL,
        watched_seconds INTEGER DEFAULT 0 NOT NULL,
        video_completed INTEGER DEFAULT 0 NOT NULL,
        quiz_passed INTEGER DEFAULT 0 NOT NULL,
        quiz_score INTEGER DEFAULT 0,
        completed_at TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL,
        UNIQUE(user_id, lesson_id)
    );

    CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_progress_user ON lesson_progress(user_id);
`);

console.log('✅ Done!');
db.close();
```

**Run with:**
```bash
bun run scripts/setup-db.ts
```

### Schema Changes

When you need to change the schema:

1. **Development**: Delete the .db file and re-run setup
2. **Production with data**: Write ALTER TABLE script
3. **Complex changes**: Backup, migrate, restore

---

## 5.5 Connecting Multiple Databases

Here's how we connect both databases.

### Connection Module

Create `src/lib/server/db/index.ts`:

```typescript
import { drizzle } from 'drizzle-orm/bun-sqlite';
import { Database } from 'bun:sqlite';
import { resolve } from 'path';

// Import schemas
import * as userSchema from './schema';
import * as contentSchema from './schema-content';

// Resolve paths
const dataDir = resolve(process.cwd(), 'data');

// ============================================
// USER DATABASE (Read-Write)
// ============================================

const usersSqlite = new Database(resolve(dataDir, 'users.db'));
usersSqlite.exec('PRAGMA journal_mode = WAL');
usersSqlite.exec('PRAGMA busy_timeout = 5000');
usersSqlite.exec('PRAGMA synchronous = NORMAL');
usersSqlite.exec('PRAGMA foreign_keys = ON');

export const db = drizzle(usersSqlite, { schema: userSchema });

// ============================================
// CONTENT DATABASE (Read-Mostly)
// ============================================

const contentSqlite = new Database(resolve(dataDir, 'content.db'));
contentSqlite.exec('PRAGMA foreign_keys = ON');

export const contentDatabase = drizzle(contentSqlite, { schema: contentSchema });

// ============================================
// RE-EXPORTS
// ============================================

// Re-export schemas for convenience
export * from './schema';
export * from './schema-content';
```

### Usage in SvelteKit

```typescript
// In +page.server.ts
import { db, contentDatabase, users, lessons } from '$lib/server/db';

export async function load() {
    // Query user database
    const allUsers = db.select().from(users).all();
    
    // Query content database
    const allLessons = contentDatabase.select().from(lessons).all();
    
    return { users: allUsers, lessons: allLessons };
}
```

---

## 5.6 Query Optimization

Write efficient queries from the start.

### Use Specific Selects

```typescript
// ❌ Bad: Fetches all columns
const lessons = contentDatabase.select().from(lessons).all();

// ✅ Good: Only fetches needed columns
const lessons = contentDatabase
    .select({
        id: lessons.id,
        title: lessons.title,
        slug: lessons.slug,
    })
    .from(lessons)
    .all();
```

### Use Limits

```typescript
// Always limit when you don't need all results
const recent = contentDatabase
    .select()
    .from(lessons)
    .orderBy(desc(lessons.createdAt))
    .limit(10)
    .all();
```

### Use Joins Instead of N+1

```typescript
// ❌ Bad: N+1 queries
const lessons = contentDatabase.select().from(lessons).all();
for (const lesson of lessons) {
    const track = contentDatabase
        .select()
        .from(tracks)
        .where(eq(tracks.id, lesson.trackId))
        .get();
}

// ✅ Good: Single join query
const lessonsWithTrack = contentDatabase
    .select()
    .from(lessons)
    .leftJoin(tracks, eq(lessons.trackId, tracks.id))
    .all();
```

### Count Queries

```typescript
import { count } from 'drizzle-orm';

// Get count efficiently
const result = contentDatabase
    .select({ count: count() })
    .from(lessons)
    .where(eq(lessons.isPublished, true))
    .get();

const total = result?.count ?? 0;
```

### Aggregations

```typescript
import { count, sql } from 'drizzle-orm';

// Count lessons per track
const stats = contentDatabase
    .select({
        trackId: lessons.trackId,
        lessonCount: count(),
    })
    .from(lessons)
    .groupBy(lessons.trackId)
    .all();
```

---

## Summary

In this chapter, we set up Drizzle ORM:

| Topic | Key Points |
|-------|------------|
| Schemas | Declarative, type-safe definitions |
| Queries | SQL-like syntax with full TypeScript support |
| Connections | Dual database setup with proper pragmas |
| Optimization | Specific selects, limits, joins |

Our data layer is now complete. Next, we'll build the authentication system on top of it.

---

> **Next Chapter**: [Chapter 6: Authentication System](./chapter-06-authentication.md)
