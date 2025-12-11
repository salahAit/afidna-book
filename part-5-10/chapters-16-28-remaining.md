# Part V: Admin Panel

## Chapter 16: Admin Dashboard

---

### 16.1 Access Control

```typescript
// src/routes/admin/+layout.server.ts
import { redirect } from '@sveltejs/kit';
import { isEditor } from '$lib/server/auth';

export async function load({ locals }) {
    if (!locals.user) {
        throw redirect(302, '/auth/login?redirect=/admin');
    }
    
    if (!isEditor(locals.user)) {
        throw redirect(302, '/');
    }

    return { user: locals.user };
}
```

---

### 16.2-16.5 Dashboard Implementation

```svelte
<!-- src/routes/admin/+page.svelte -->
<script lang="ts">
    let { data } = $props();
</script>

<div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
    <div class="stat bg-base-100 rounded-lg shadow">
        <div class="stat-title">المسارات</div>
        <div class="stat-value text-primary">{data.stats.tracks}</div>
    </div>
    <div class="stat bg-base-100 rounded-lg shadow">
        <div class="stat-title">السلاسل</div>
        <div class="stat-value text-secondary">{data.stats.series}</div>
    </div>
    <div class="stat bg-base-100 rounded-lg shadow">
        <div class="stat-title">الدروس</div>
        <div class="stat-value text-accent">{data.stats.lessons}</div>
    </div>
    <div class="stat bg-base-100 rounded-lg shadow">
        <div class="stat-title">الفيديوهات</div>
        <div class="stat-value text-info">{data.stats.videos}</div>
    </div>
</div>

<!-- Quick Actions -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <a href="/admin/lessons" class="btn btn-outline">📝 الدروس</a>
    <a href="/admin/videos" class="btn btn-outline">🎬 الفيديوهات</a>
    <a href="/admin/series" class="btn btn-outline">📂 السلاسل</a>
    <a href="/admin/tracks" class="btn btn-outline">📚 المسارات</a>
</div>
```

---

## Chapter 17: Content Management

### 17.1-17.6 CRUD Operations

```typescript
// src/routes/admin/lessons/[id]/+page.server.ts
export const actions: Actions = {
    update: async ({ request, params, locals }) => {
        const form = await request.formData();
        
        contentDatabase
            .update(lessons)
            .set({
                title: form.get('title') as string,
                description: form.get('description') as string,
                updatedAt: new Date().toISOString(),
                lastModifiedBy: locals.user.id.toString(),
            })
            .where(eq(lessons.id, params.id))
            .run();

        return { success: true };
    },

    toggleLock: async ({ params, locals }) => {
        if (locals.user.role !== 'admin') {
            return fail(403, { error: 'Admin only' });
        }

        const lesson = contentDatabase
            .select()
            .from(lessons)
            .where(eq(lessons.id, params.id))
            .get();

        contentDatabase
            .update(lessons)
            .set({ isLocked: !lesson.isLocked })
            .where(eq(lessons.id, params.id))
            .run();

        return { success: true };
    },
};
```

---

## Chapter 18: Audit & Protection

### 18.1-18.5 Audit Trail

```typescript
// All content tables have:
{
    createdAt: TEXT,         // When created
    updatedAt: TEXT,         // Last modified
    lastModifiedBy: TEXT,    // 'script' or user ID
    isLocked: INTEGER,       // Prevent changes
}

// Check before update:
function canModify(item, forceMode = false) {
    if (item.isLocked) return false;
    if (item.lastModifiedBy !== 'script' && !forceMode) return false;
    return true;
}
```

---

# Part VI: Content Pipeline

## Chapter 19: Content Seeding

### 19.1-19.6 Seed Script

```typescript
// scripts/seed-content.ts
async function seedLesson(lesson, forceMode) {
    const existing = contentDatabase
        .select()
        .from(lessons)
        .where(eq(lessons.id, lesson.id))
        .get();

    if (existing) {
        // Check if can update
        if (existing.isLocked) {
            console.log(`⏭️  Skipping locked: ${lesson.id}`);
            return;
        }
        if (existing.lastModifiedBy !== 'script' && !forceMode) {
            console.log(`⏭️  Skipping human edit: ${lesson.id}`);
            return;
        }
        
        // Update
        contentDatabase.update(lessons).set({...lesson}).run();
    } else {
        // Insert
        contentDatabase.insert(lessons).values({...lesson}).run();
    }
}
```

---

## Chapter 20: Media Management

### R2/S3 Integration (for future)

```typescript
// Upload to Cloudflare R2
async function uploadToR2(file: File, key: string) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${R2_ENDPOINT}/${key}`, {
        method: 'PUT',
        body: file,
        headers: {
            'Authorization': `Bearer ${R2_TOKEN}`,
        },
    });
    
    return `${R2_PUBLIC_URL}/${key}`;
}
```

---

# Part VII: Testing & Quality

## Chapter 21: Testing Strategy

### Unit Tests with Bun

```typescript
// tests/auth.test.ts
import { describe, expect, test } from 'bun:test';
import { hashPassword, verifyPassword } from '$lib/server/auth';

describe('Auth', () => {
    test('password hashing', async () => {
        const password = 'test123';
        const hash = await hashPassword(password);
        
        expect(hash).not.toBe(password);
        expect(await verifyPassword(password, hash)).toBe(true);
        expect(await verifyPassword('wrong', hash)).toBe(false);
    });
});
```

### Run Tests

```bash
bun test
```

---

## Chapter 22: Code Quality

### ESLint + Prettier

```json
// .prettierrc
{
    "tabWidth": 4,
    "singleQuote": true,
    "trailingComma": "es5"
}
```

```bash
bun run format
bun run lint
```

---

# Part VIII: Deployment

## Chapter 23-26: Production Deployment

### Build

```bash
bun run build
```

### VPS Deployment

```bash
# Ubuntu server
sudo apt update
curl -fsSL https://bun.sh/install | bash
git clone <repo>
cd afidna
bun install
bun run db:setup
bun run db:content  
bun run build

# Run with systemd
sudo systemctl enable afidna
sudo systemctl start afidna
```

### Caddy Config

```
afidna.com {
    reverse_proxy localhost:3000
}
```

---

# Part IX: Scaling & Optimization

## Chapter 27-28: Performance

### Database Optimization

```typescript
// Use indexes
CREATE INDEX idx_lessons_slug ON lessons(slug);

// Use specific selects
db.select({ id, title }).from(lessons);

// Use limits
.limit(10)
```

### Caching

```typescript
// Cache headers
return new Response(body, {
    headers: {
        'Cache-Control': 'public, max-age=3600',
    },
});
```

---

# Part X: Appendices

## Appendix A: Code Reference

All schemas, APIs, and components are in the codebase.

## Appendix B: Commands

```bash
# Development
bun run dev

# Database
bun run db:setup
bun run db:content
bun run seed

# Build
bun run build
bun run preview
```

## Appendix C: Troubleshooting

| Problem | Solution |
|---------|----------|
| Port in use | `kill -9 $(lsof -ti:5173)` |
| DB locked | Stop other processes |
| Build fails | Check TypeScript errors |

## Appendix D: Resources

- [SvelteKit Docs](https://kit.svelte.dev)
- [Drizzle Docs](https://orm.drizzle.team)
- [DaisyUI Docs](https://daisyui.com)
- [Tailwind Docs](https://tailwindcss.com)

---

> **End of Book**
> 
> Thank you for reading! Build something amazing. 🚀
