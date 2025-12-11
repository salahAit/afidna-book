# Chapter 12: Video Player Integration

---

## 12.1 YouTube IFrame API

We'll embed YouTube videos with full control over playback.

### Loading the API

```typescript
// src/lib/utils/youtube.ts
let apiLoaded = false;
let apiLoadPromise: Promise<void> | null = null;

export function loadYouTubeAPI(): Promise<void> {
    if (apiLoaded) return Promise.resolve();
    if (apiLoadPromise) return apiLoadPromise;

    apiLoadPromise = new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = 'https://www.youtube.com/iframe_api';
        
        (window as any).onYouTubeIframeAPIReady = () => {
            apiLoaded = true;
            resolve();
        };
        
        document.head.appendChild(script);
    });

    return apiLoadPromise;
}
```

### API Reference

```typescript
interface YT.Player {
    playVideo(): void;
    pauseVideo(): void;
    seekTo(seconds: number): void;
    getCurrentTime(): number;
    getDuration(): number;
    getPlayerState(): number;
}

// Player States
const PlayerState = {
    UNSTARTED: -1,
    ENDED: 0,
    PLAYING: 1,
    PAUSED: 2,
    BUFFERING: 3,
    CUED: 5,
};
```

---

## 12.2 Building VideoPlayer Component

```svelte
<!-- src/lib/components/VideoPlayer.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { loadYouTubeAPI } from '$lib/utils/youtube';
    import { browser } from '$app/environment';

    interface Props {
        youtubeId: string;
        title?: string;
        startTime?: number;
        onProgress?: (seconds: number) => void;
        onComplete?: () => void;
    }

    let { 
        youtubeId, 
        title = 'Video',
        startTime = 0,
        onProgress,
        onComplete 
    }: Props = $props();

    let containerRef: HTMLDivElement;
    let player: YT.Player | null = null;
    let progressInterval: number | null = null;
    let lastReportedTime = 0;

    onMount(async () => {
        if (!browser || !youtubeId) return;
        
        await loadYouTubeAPI();
        initPlayer();
    });

    onDestroy(() => {
        if (progressInterval) clearInterval(progressInterval);
        player?.destroy();
    });

    function initPlayer() {
        player = new YT.Player(containerRef, {
            videoId: youtubeId,
            playerVars: {
                autoplay: 0,
                modestbranding: 1,
                rel: 0,
                start: Math.floor(startTime),
            },
            events: {
                onReady: handleReady,
                onStateChange: handleStateChange,
            },
        });
    }

    function handleReady() {
        console.log('Player ready');
    }

    function handleStateChange(event: YT.OnStateChangeEvent) {
        const state = event.data;

        if (state === YT.PlayerState.PLAYING) {
            startProgressTracking();
        } else if (state === YT.PlayerState.PAUSED) {
            stopProgressTracking();
        } else if (state === YT.PlayerState.ENDED) {
            stopProgressTracking();
            onComplete?.();
        }
    }

    function startProgressTracking() {
        if (progressInterval) return;
        
        progressInterval = setInterval(() => {
            if (!player) return;
            
            const currentTime = player.getCurrentTime();
            
            // Report every 30 seconds
            if (currentTime - lastReportedTime >= 30) {
                lastReportedTime = currentTime;
                onProgress?.(currentTime);
            }
        }, 5000) as unknown as number;
    }

    function stopProgressTracking() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
        
        // Report final time
        if (player) {
            onProgress?.(player.getCurrentTime());
        }
    }
</script>

<div class="video-player">
    <div class="aspect-video bg-black rounded-lg overflow-hidden">
        <div bind:this={containerRef} class="w-full h-full"></div>
    </div>
    {#if title}
        <h3 class="text-lg font-bold mt-3">{title}</h3>
    {/if}
</div>
```

---

## 12.3 Progress Tracking

### The 10-Minute Rule

```typescript
// src/lib/utils/progress.ts

const TEN_MINUTES = 600; // seconds

export function shouldMarkComplete(
    watchedSeconds: number,
    videoDuration: number
): boolean {
    // Complete if watched 10+ minutes OR reached end
    return watchedSeconds >= TEN_MINUTES || 
           watchedSeconds >= videoDuration * 0.9;
}
```

### Reporting Progress

```typescript
async function reportProgress(lessonId: string, seconds: number) {
    try {
        await fetch('/api/progress', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lessonId,
                watchedSeconds: Math.floor(seconds),
            }),
        });
    } catch (error) {
        console.error('Failed to report progress:', error);
    }
}
```

---

## 12.4 Handling Events

```svelte
<script>
    function handleProgress(seconds: number) {
        // Save progress
        reportProgress(lesson.id, seconds);
    }

    function handleComplete() {
        // Mark as complete
        fetch('/api/progress', {
            method: 'POST',
            body: JSON.stringify({
                lessonId: lesson.id,
                videoCompleted: true,
            }),
        });
        
        // Move to next video or show quiz
        if (hasQuiz) {
            showQuiz = true;
        } else if (nextVideo) {
            currentVideoIndex++;
        }
    }
</script>

<VideoPlayer
    youtubeId={video.youtubeId}
    title={video.title}
    startTime={progress?.watchedSeconds || 0}
    {onProgress}
    onComplete={handleComplete}
/>
```

---

## 12.5-12.7 Advanced Features

### Quality Selection (handled by YouTube)

YouTube automatically handles quality based on connection.

### Fullscreen Support

```svelte
<button 
    class="btn btn-ghost btn-sm"
    onclick={() => containerRef.requestFullscreen()}
>
    ⛶ Fullscreen
</button>
```

---

# Chapter 13: Interactive Quiz System

---

## 13.1 Quiz Data Structure

```typescript
interface Question {
    id: string;
    text: string;
    options: string[];
    correctIndex: number;
    points?: number;
}

interface Quiz {
    questions: Question[];
    passingScore: number; // percentage
}
```

### Storing in Database

```sql
-- In videos table
quiz TEXT  -- JSON array of questions
```

---

## 13.2-13.7 Quiz Component

See `src/lib/components/Quiz.svelte` for the full implementation:

- Multiple choice with A/B/C/D options
- Instant feedback (correct/incorrect)
- Score calculation
- Pass/fail determination
- Automatic progression

---

# Chapter 14: Progress Tracking

---

## 14.1-14.6 Progress System

### Database Schema

```sql
CREATE TABLE lesson_progress (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    lesson_id TEXT NOT NULL,
    watched_seconds INTEGER DEFAULT 0,
    video_completed INTEGER DEFAULT 0,
    quiz_passed INTEGER DEFAULT 0,
    quiz_score INTEGER DEFAULT 0,
    updated_at TEXT,
    UNIQUE(user_id, lesson_id)
);
```

### UPSERT Logic

```typescript
// Check if exists
const existing = db.select()...

if (existing) {
    db.update(lessonProgress)
        .set({ 
            watchedSeconds: Math.max(existing.watchedSeconds, newSeconds),
            ...
        })
        .where(eq(lessonProgress.id, existing.id));
} else {
    db.insert(lessonProgress).values({...});
}
```

---

# Chapter 15: Global Search

---

## 15.1-15.6 Search Implementation

### SQLite LIKE Search

```typescript
const pattern = `%${query}%`;

const results = contentDatabase
    .select()
    .from(lessons)
    .where(or(
        like(lessons.title, pattern),
        like(lessons.description, pattern)
    ))
    .all();
```

### Search Page

```svelte
<form onsubmit={handleSearch}>
    <input bind:value={query} placeholder="Search..." />
    <button>Search</button>
</form>

{#each results.lessons as lesson}
    <LessonCard {lesson} />
{/each}
```

---

> **Next Part**: [Part V → Chapter 16: Admin Dashboard](../part-5/chapter-16-admin.md)
