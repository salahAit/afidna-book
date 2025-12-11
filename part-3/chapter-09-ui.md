# Chapter 9: UI with DaisyUI & Tailwind

---

## 9.1 Setting Up Tailwind CSS 4

Tailwind v4 brings a simpler setup.

### Installation

```bash
bun add -d tailwindcss @tailwindcss/vite
```

### Vite Configuration

```typescript
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [
        tailwindcss(),
        sveltekit()
    ]
});
```

### CSS Entry Point

```css
/* src/app.css */
@import 'tailwindcss';
```

### Import in Layout

```svelte
<!-- src/routes/+layout.svelte -->
<script>
    import '../app.css';
</script>
```

### Tailwind Basics

```html
<!-- Spacing -->
<div class="p-4 m-2">Padding 4, Margin 2</div>

<!-- Flexbox -->
<div class="flex items-center justify-between">...</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">...</div>

<!-- Colors -->
<div class="bg-blue-500 text-white">Blue background</div>

<!-- Responsive -->
<div class="text-sm md:text-base lg:text-lg">Responsive text</div>
```

---

## 9.2 DaisyUI Components

DaisyUI adds beautiful, ready-to-use components.

### Installation

```bash
bun add -d daisyui
```

### Configuration

```css
/* src/app.css */
@import 'tailwindcss';
@plugin 'daisyui';
```

### Core Components

**Buttons:**
```html
<button class="btn">Default</button>
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-sm">Small</button>
<button class="btn btn-lg">Large</button>
```

**Cards:**
```html
<div class="card bg-base-100 shadow-xl">
    <figure><img src="/image.jpg" alt="Cover" /></figure>
    <div class="card-body">
        <h2 class="card-title">Title</h2>
        <p>Description</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>
```

**Badges:**
```html
<span class="badge">Default</span>
<span class="badge badge-primary">Primary</span>
<span class="badge badge-lg">Large</span>
```

**Alerts:**
```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-error">Error message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-info">Info message</div>
```

**Form Controls:**
```html
<input type="text" class="input input-bordered w-full" />
<select class="select select-bordered">
    <option>Option 1</option>
</select>
<textarea class="textarea textarea-bordered"></textarea>
```

**Navigation:**
```html
<div class="navbar bg-base-100">
    <div class="flex-1">
        <a class="btn btn-ghost text-xl">Brand</a>
    </div>
    <div class="flex-none">
        <ul class="menu menu-horizontal px-1">
            <li><a>Link 1</a></li>
            <li><a>Link 2</a></li>
        </ul>
    </div>
</div>
```

---

## 9.3 Theme System (Light/Dark)

DaisyUI includes multiple themes.

### Available Themes

```
light, dark, cupcake, bumblebee, emerald, corporate, 
synthwave, retro, cyberpunk, valentine, halloween, 
garden, forest, aqua, lofi, pastel, fantasy, wireframe, 
black, luxury, dracula, cmyk, autumn, business, acid, 
lemonade, night, coffee, winter, dim, nord, sunset
```

### Setting Theme

```html
<!-- In app.html -->
<html data-theme="dark">
```

### Dynamic Theme Switching

```svelte
<!-- ThemeSwitcher.svelte -->
<script lang="ts">
    import { browser } from '$app/environment';
    
    let theme = $state(
        browser ? localStorage.getItem('theme') || 'light' : 'light'
    );

    function toggleTheme() {
        theme = theme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
</script>

<button class="btn btn-ghost" onclick={toggleTheme}>
    {theme === 'light' ? '🌙' : '☀️'}
</button>
```

### Initialize Theme

```svelte
<!-- +layout.svelte -->
<script>
    import { browser } from '$app/environment';
    import { onMount } from 'svelte';

    onMount(() => {
        const saved = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', saved);
    });
</script>
```

---

## 9.4 RTL Support for Arabic

Arabic text flows right-to-left.

### HTML Direction

```html
<!-- app.html -->
<html lang="ar" dir="rtl">
```

### Dynamic Direction

```svelte
<script>
    let locale = $state('ar');
</script>

<svelte:body dir={locale === 'ar' ? 'rtl' : 'ltr'} />
```

### RTL Utilities

```css
/* src/app.css */
@layer utilities {
    /* Flip margins/paddings */
    [dir="rtl"] .ml-4 {
        margin-left: 0;
        margin-right: 1rem;
    }
    
    /* Text alignment */
    [dir="rtl"] {
        text-align: right;
    }
}
```

### Logical Properties (CSS)

Modern CSS supports logical properties:

```css
/* Instead of margin-left/right */
.element {
    margin-inline-start: 1rem;  /* Left in LTR, Right in RTL */
    margin-inline-end: 1rem;    /* Right in LTR, Left in RTL */
}
```

### DaisyUI RTL

DaisyUI works well with RTL. Just set `dir="rtl"`:

```svelte
<div class="navbar bg-base-100" dir="rtl">
    <!-- Components auto-adjust -->
</div>
```

---

## 9.5 Responsive Design Patterns

Mobile-first approach.

### Breakpoints

| Prefix | Width | Devices |
|--------|-------|---------|
| (none) | < 640px | Mobile |
| `sm:` | ≥ 640px | Large phones |
| `md:` | ≥ 768px | Tablets |
| `lg:` | ≥ 1024px | Laptops |
| `xl:` | ≥ 1280px | Desktops |
| `2xl:` | ≥ 1536px | Large screens |

### Common Patterns

**Responsive Grid:**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <!-- 1 col on mobile, 2 on tablet, 3 on desktop -->
</div>
```

**Hidden on Mobile:**
```html
<div class="hidden md:block">Desktop only</div>
<div class="md:hidden">Mobile only</div>
```

**Responsive Text:**
```html
<h1 class="text-2xl md:text-4xl lg:text-5xl">Responsive Title</h1>
```

**Responsive Padding:**
```html
<div class="p-4 md:p-8 lg:p-12">Grows with screen</div>
```

### Mobile Navigation Pattern

```svelte
<script>
    let isMenuOpen = $state(false);
</script>

<!-- Desktop Nav -->
<nav class="hidden md:flex gap-4">
    <a href="/">Home</a>
    <a href="/tracks">Tracks</a>
</nav>

<!-- Mobile Menu Button -->
<button class="md:hidden" onclick={() => isMenuOpen = !isMenuOpen}>
    ☰
</button>

<!-- Mobile Drawer -->
{#if isMenuOpen}
    <div class="fixed inset-0 z-50 md:hidden">
        <div class="bg-black/50" onclick={() => isMenuOpen = false}></div>
        <nav class="fixed right-0 top-0 h-full w-64 bg-base-100 p-4">
            <a href="/">Home</a>
            <a href="/tracks">Tracks</a>
        </nav>
    </div>
{/if}
```

---

## 9.6 Custom Component Library

Build reusable components with consistent styling.

### Button Component

```svelte
<!-- src/lib/components/Button.svelte -->
<script lang="ts">
    interface Props {
        variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
        size?: 'sm' | 'md' | 'lg';
        loading?: boolean;
        disabled?: boolean;
        type?: 'button' | 'submit';
        onclick?: () => void;
    }

    let {
        variant = 'primary',
        size = 'md',
        loading = false,
        disabled = false,
        type = 'button',
        onclick,
        children,
    }: Props & { children: any } = $props();

    const variantClasses = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        ghost: 'btn-ghost',
        outline: 'btn-outline',
    };

    const sizeClasses = {
        sm: 'btn-sm',
        md: '',
        lg: 'btn-lg',
    };
</script>

<button
    {type}
    class="btn {variantClasses[variant]} {sizeClasses[size]}"
    disabled={disabled || loading}
    {onclick}
>
    {#if loading}
        <span class="loading loading-spinner loading-sm"></span>
    {/if}
    {@render children()}
</button>
```

### Card Component

```svelte
<!-- src/lib/components/Card.svelte -->
<script lang="ts">
    interface Props {
        title?: string;
        image?: string;
        href?: string;
        class?: string;
    }

    let { title, image, href, class: className = '', children }: Props & { children: any } = $props();
</script>

<svelte:element 
    this={href ? 'a' : 'div'}
    {href}
    class="card bg-base-100 shadow-lg hover:shadow-xl transition-shadow {className}"
>
    {#if image}
        <figure>
            <img src={image} alt={title || ''} class="w-full h-48 object-cover" />
        </figure>
    {/if}
    <div class="card-body">
        {#if title}
            <h3 class="card-title">{title}</h3>
        {/if}
        {@render children()}
    </div>
</svelte:element>
```

### Input Component

```svelte
<!-- src/lib/components/Input.svelte -->
<script lang="ts">
    interface Props {
        label?: string;
        name: string;
        type?: 'text' | 'email' | 'password' | 'number';
        placeholder?: string;
        value?: string;
        error?: string;
        required?: boolean;
    }

    let {
        label,
        name,
        type = 'text',
        placeholder,
        value = '',
        error,
        required = false,
    }: Props = $props();
</script>

<div class="form-control w-full">
    {#if label}
        <label class="label" for={name}>
            <span class="label-text">{label}</span>
            {#if required}
                <span class="text-error">*</span>
            {/if}
        </label>
    {/if}
    
    <input
        {type}
        {name}
        id={name}
        {placeholder}
        {value}
        {required}
        class="input input-bordered w-full {error ? 'input-error' : ''}"
    />
    
    {#if error}
        <label class="label">
            <span class="label-text-alt text-error">{error}</span>
        </label>
    {/if}
</div>
```

### Usage

```svelte
<script>
    import Button from '$lib/components/Button.svelte';
    import Card from '$lib/components/Card.svelte';
    import Input from '$lib/components/Input.svelte';
</script>

<Button variant="primary" loading={isSubmitting}>
    Submit
</Button>

<Card title="Lesson Title" image="/cover.jpg" href="/lessons/1">
    <p>Lesson description...</p>
</Card>

<Input
    label="Email"
    name="email"
    type="email"
    error={form?.errors?.email}
    required
/>
```

---

## Summary

| Topic | Key Points |
|-------|------------|
| Tailwind | Utility-first, v4 simpler setup |
| DaisyUI | Ready components, themes |
| Themes | `data-theme` attribute, localStorage |
| RTL | `dir="rtl"`, logical CSS properties |
| Responsive | Mobile-first, breakpoint prefixes |
| Components | Reusable, typed props |

Our UI foundation is ready. Next: building the actual pages.

---

> **Next Chapter**: [Chapter 10: Building Core Pages](./chapter-10-pages.md)
