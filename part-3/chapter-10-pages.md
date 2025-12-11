# Chapter 10: Building Core Pages

---

## 10.1 Homepage with Dynamic Stats

The homepage is your platform's first impression.

### Load Function

```typescript
// src/routes/+page.server.ts
import type { PageServerLoad } from './$types';
import { contentDatabase, tracks, series, lessons, videos } from '$lib/server/db';
import { count, eq, desc } from 'drizzle-orm';

export const load: PageServerLoad = async () => {
    // Get counts
    const tracksCount = contentDatabase
        .select({ count: count() })
        .from(tracks)
        .get()?.count ?? 0;

    const seriesCount = contentDatabase
        .select({ count: count() })
        .from(series)
        .get()?.count ?? 0;

    const lessonsCount = contentDatabase
        .select({ count: count() })
        .from(lessons)
        .where(eq(lessons.isPublished, true))
        .get()?.count ?? 0;

    const videosCount = contentDatabase
        .select({ count: count() })
        .from(videos)
        .get()?.count ?? 0;

    // Get latest lessons
    const latestLessons = contentDatabase
        .select()
        .from(lessons)
        .where(eq(lessons.isPublished, true))
        .orderBy(desc(lessons.createdAt))
        .limit(6)
        .all();

    // Get all tracks for display
    const allTracks = contentDatabase
        .select()
        .from(tracks)
        .orderBy(tracks.order)
        .all();

    return {
        stats: {
            tracks: tracksCount,
            series: seriesCount,
            lessons: lessonsCount,
            videos: videosCount,
        },
        latestLessons,
        tracks: allTracks,
    };
};
```

### Homepage Component

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
    import type { PageData } from './$types';
    import { getTrackColor, getTrackIcon } from '$lib/theme';
    
    let { data }: { data: PageData } = $props();
</script>

<svelte:head>
    <title>أفدنا - منصة تعليمية إسلامية</title>
</svelte:head>

<!-- Hero Section -->
<section class="hero min-h-[70vh] bg-gradient-to-br from-primary to-primary-focus text-primary-content">
    <div class="hero-content text-center">
        <div class="max-w-2xl">
            <h1 class="text-5xl font-bold mb-6">
                أفدنا بما علّمك الله
            </h1>
            <p class="text-xl mb-8 opacity-90">
                منصة تعليمية لنشر العلم الشرعي النافع
            </p>
            <div class="flex gap-4 justify-center">
                <a href="/tracks" class="btn btn-secondary btn-lg">
                    ابدأ التعلم
                </a>
                <a href="/about" class="btn btn-ghost btn-lg">
                    معرفة المزيد
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Stats Section -->
<section class="py-16 bg-base-200">
    <div class="container mx-auto px-4">
        <div class="stats stats-vertical lg:stats-horizontal shadow w-full">
            <div class="stat">
                <div class="stat-figure text-primary text-3xl">📚</div>
                <div class="stat-title">المسارات</div>
                <div class="stat-value text-primary">{data.stats.tracks}</div>
            </div>
            <div class="stat">
                <div class="stat-figure text-secondary text-3xl">📂</div>
                <div class="stat-title">السلاسل</div>
                <div class="stat-value text-secondary">{data.stats.series}</div>
            </div>
            <div class="stat">
                <div class="stat-figure text-accent text-3xl">📝</div>
                <div class="stat-title">الدروس</div>
                <div class="stat-value text-accent">{data.stats.lessons}</div>
            </div>
            <div class="stat">
                <div class="stat-figure text-info text-3xl">🎬</div>
                <div class="stat-title">الفيديوهات</div>
                <div class="stat-value text-info">{data.stats.videos}</div>
            </div>
        </div>
    </div>
</section>

<!-- Tracks Section -->
<section class="py-16 bg-base-100">
    <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">المسارات التعليمية</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each data.tracks as track}
                <a 
                    href="/tracks/{track.id}"
                    class="card bg-gradient-to-br {getTrackColor(track.id)} text-white shadow-lg hover:scale-105 transition-transform"
                >
                    <div class="card-body">
                        <span class="text-4xl">{getTrackIcon(track.id, track.icon)}</span>
                        <h3 class="card-title text-white">{track.title}</h3>
                        {#if track.description}
                            <p class="opacity-90">{track.description}</p>
                        {/if}
                    </div>
                </a>
            {/each}
        </div>
    </div>
</section>

<!-- Latest Lessons -->
<section class="py-16 bg-base-200">
    <div class="container mx-auto px-4">
        <h2 class="text-3xl font-bold text-center mb-12">أحدث الدروس</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each data.latestLessons as lesson}
                <a href="/lessons/{lesson.slug}" class="card bg-base-100 shadow-lg hover:shadow-xl transition-shadow">
                    <div class="card-body">
                        <h3 class="card-title">{lesson.title}</h3>
                        {#if lesson.description}
                            <p class="text-base-content/70 line-clamp-2">{lesson.description}</p>
                        {/if}
                        {#if lesson.instructor}
                            <p class="text-sm text-base-content/60">👨‍🏫 {lesson.instructor}</p>
                        {/if}
                    </div>
                </a>
            {/each}
        </div>
        
        <div class="text-center mt-8">
            <a href="/lessons" class="btn btn-primary">
                عرض جميع الدروس
            </a>
        </div>
    </div>
</section>
```

---

## 10.2 Content Listing (Tracks, Lessons)

List pages with filtering and search.

### Tracks Listing

```typescript
// src/routes/tracks/+page.server.ts
export const load: PageServerLoad = async () => {
    const allTracks = contentDatabase
        .select()
        .from(tracks)
        .orderBy(tracks.order)
        .all();

    // Get lesson count per track
    const tracksWithCount = allTracks.map(track => {
        const lessonCount = contentDatabase
            .select({ count: count() })
            .from(lessons)
            .where(and(
                eq(lessons.trackId, track.id),
                eq(lessons.isPublished, true)
            ))
            .get()?.count ?? 0;

        return { ...track, lessonCount };
    });

    return { tracks: tracksWithCount };
};
```

### Lessons Listing with Search

```svelte
<!-- src/routes/lessons/+page.svelte -->
<script lang="ts">
    import type { PageData } from './$types';
    
    let { data }: { data: PageData } = $props();
    
    let searchQuery = $state('');
    let selectedTrack = $state('all');
    
    const filteredLessons = $derived(
        data.lessons.filter(lesson => {
            const matchesSearch = lesson.title.toLowerCase()
                .includes(searchQuery.toLowerCase());
            const matchesTrack = selectedTrack === 'all' || 
                lesson.trackId === selectedTrack;
            return matchesSearch && matchesTrack;
        })
    );
</script>

<section class="py-8">
    <div class="container mx-auto px-4">
        <!-- Filters -->
        <div class="card bg-base-100 shadow mb-8">
            <div class="card-body">
                <div class="flex flex-wrap gap-4 items-center">
                    <input
                        type="text"
                        bind:value={searchQuery}
                        placeholder="ابحث عن درس..."
                        class="input input-bordered flex-1 min-w-[200px]"
                    />
                    
                    <select bind:value={selectedTrack} class="select select-bordered">
                        <option value="all">كل المسارات</option>
                        {#each data.tracks as track}
                            <option value={track.id}>{track.title}</option>
                        {/each}
                    </select>
                    
                    <span class="badge badge-lg">
                        {filteredLessons.length} درس
                    </span>
                </div>
            </div>
        </div>

        <!-- Lessons Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each filteredLessons as lesson}
                <a href="/lessons/{lesson.slug}" class="card bg-base-100 shadow hover:shadow-lg transition-shadow">
                    <div class="card-body">
                        <h3 class="card-title">{lesson.title}</h3>
                        <p class="text-sm text-base-content/70 line-clamp-2">
                            {lesson.description || 'لا يوجد وصف'}
                        </p>
                    </div>
                </a>
            {/each}
        </div>

        {#if filteredLessons.length === 0}
            <div class="text-center py-16">
                <span class="text-6xl mb-4 block">😕</span>
                <h3 class="text-xl font-bold">لا توجد نتائج</h3>
                <p class="text-base-content/70">جرب كلمات بحث مختلفة</p>
            </div>
        {/if}
    </div>
</section>
```

---

## 10.3 Detail Pages

Single item pages with rich content.

### Single Track Page

```typescript
// src/routes/tracks/[id]/+page.server.ts
export const load: PageServerLoad = async ({ params }) => {
    const track = contentDatabase
        .select()
        .from(tracks)
        .where(eq(tracks.id, params.id))
        .get();

    if (!track) {
        throw error(404, 'Track not found');
    }

    // Get series in this track
    const trackSeries = contentDatabase
        .select()
        .from(series)
        .where(eq(series.trackId, params.id))
        .orderBy(series.order)
        .all();

    // Get standalone lessons (no series)
    const standaloneLessons = contentDatabase
        .select()
        .from(lessons)
        .where(and(
            eq(lessons.trackId, params.id),
            isNull(lessons.seriesId),
            eq(lessons.isPublished, true)
        ))
        .orderBy(lessons.order)
        .all();

    return {
        track,
        series: trackSeries,
        standaloneLessons,
    };
};
```

### Single Lesson Page

See Chapter 12 for the full VideoPlayer integration.

---

## 10.4 Search Functionality

Global search across all content.

```typescript
// src/routes/search/+page.server.ts
export const load: PageServerLoad = async ({ url }) => {
    const query = url.searchParams.get('q')?.trim() || '';
    
    if (query.length < 2) {
        return { query: '', results: { lessons: [], tracks: [] } };
    }

    const pattern = `%${query}%`;

    const lessonResults = contentDatabase
        .select()
        .from(lessons)
        .where(and(
            eq(lessons.isPublished, true),
            or(
                like(lessons.title, pattern),
                like(lessons.description, pattern)
            )
        ))
        .limit(20)
        .all();

    const trackResults = contentDatabase
        .select()
        .from(tracks)
        .where(or(
            like(tracks.title, pattern),
            like(tracks.description, pattern)
        ))
        .all();

    return {
        query,
        results: {
            lessons: lessonResults,
            tracks: trackResults,
        },
    };
};
```

```svelte
<!-- src/routes/search/+page.svelte -->
<script lang="ts">
    import { goto } from '$app/navigation';
    
    let { data } = $props();
    let searchInput = $state(data.query);

    function handleSearch(e: Event) {
        e.preventDefault();
        if (searchInput.trim().length >= 2) {
            goto(`/search?q=${encodeURIComponent(searchInput)}`);
        }
    }
</script>

<form onsubmit={handleSearch} class="max-w-xl mx-auto mb-8">
    <div class="join w-full">
        <input
            type="text"
            bind:value={searchInput}
            placeholder="ابحث..."
            class="input input-bordered join-item flex-1"
        />
        <button class="btn btn-primary join-item">بحث</button>
    </div>
</form>

{#if data.results.lessons.length > 0}
    <h2 class="text-xl font-bold mb-4">الدروس</h2>
    <!-- Render lessons... -->
{/if}

{#if data.results.tracks.length > 0}
    <h2 class="text-xl font-bold mb-4">المسارات</h2>
    <!-- Render tracks... -->
{/if}
```

---

## 10.5 User Dashboard

Personal progress page.

```typescript
// src/routes/dashboard/+page.server.ts
export const load: PageServerLoad = async ({ locals }) => {
    if (!locals.user) {
        throw redirect(302, '/auth/login?redirect=/dashboard');
    }

    const progress = db
        .select()
        .from(lessonProgress)
        .where(eq(lessonProgress.userId, locals.user.id))
        .all();

    const completedCount = progress.filter(p => p.videoCompleted).length;
    const totalWatchTime = progress.reduce((sum, p) => sum + p.watchedSeconds, 0);

    return {
        user: locals.user,
        stats: {
            started: progress.length,
            completed: completedCount,
            totalMinutes: Math.floor(totalWatchTime / 60),
        },
        recentProgress: progress.slice(0, 10),
    };
};
```

---

## 10.6 Error and 404 Pages

Handle errors gracefully.

```svelte
<!-- src/routes/+error.svelte -->
<script>
    import { page } from '$app/stores';
</script>

<div class="min-h-screen flex items-center justify-center bg-base-200">
    <div class="text-center p-8">
        <div class="text-8xl mb-6">
            {#if $page.status === 404}
                🔍
            {:else if $page.status === 403}
                🔒
            {:else}
                ⚠️
            {/if}
        </div>
        
        <h1 class="text-4xl font-bold mb-4">
            {#if $page.status === 404}
                الصفحة غير موجودة
            {:else if $page.status === 403}
                غير مصرح بالوصول
            {:else}
                حدث خطأ
            {/if}
        </h1>
        
        <p class="text-base-content/70 mb-8">
            {$page.error?.message || 'حدث خطأ غير متوقع'}
        </p>
        
        <a href="/" class="btn btn-primary">
            العودة للرئيسية
        </a>
    </div>
</div>
```

---

## Summary

| Page | Features |
|------|----------|
| Homepage | Stats, tracks, latest lessons |
| Listings | Search, filter, pagination |
| Detail | Full content, related items |
| Search | Global search with results |
| Dashboard | User progress, stats |
| Error | Friendly error messages |

Core pages are complete. Next: reusable components.

---

> **Next Chapter**: [Chapter 11: Reusable Components](./chapter-11-components.md)
