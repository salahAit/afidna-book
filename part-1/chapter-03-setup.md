# Chapter 3: Setting Up the Development Environment

---

## 3.1 Installing Bun

Bun is our JavaScript runtime — think of it as a faster, more modern alternative to Node.js.

### What is Bun?

Bun is an all-in-one toolkit that includes:
- **Runtime**: Executes JavaScript/TypeScript
- **Package Manager**: Faster than npm/yarn
- **Bundler**: Built-in bundling for production
- **Test Runner**: Native testing support

### Installation

**macOS / Linux:**
```bash
curl -fsSL https://bun.sh/install | bash
```

**Windows (via WSL):**
```bash
# First, install WSL if you haven't
wsl --install

# Then install Bun in WSL
curl -fsSL https://bun.sh/install | bash
```

**Verify installation:**
```bash
bun --version
# Should output: 1.x.x
```

### Why Bun Over Node.js?

| Feature | Node.js | Bun |
|---------|---------|-----|
| Startup time | ~40ms | ~5ms |
| Package install | ~10s | ~2s |
| TypeScript | Needs transpiler | Native |
| SQLite | Needs npm package | Built-in |
| Test runner | Needs Jest/Vitest | Built-in |

---

## 3.2 Editor Setup (VS Code / Cursor)

A good editor setup will save you hours of debugging.

### VS Code Installation

Download from: https://code.visualstudio.com/

### Cursor (AI-Powered Alternative)

Cursor is VS Code with AI built-in: https://cursor.sh/

### Recommended Settings

Create `.vscode/settings.json` in your project:

```json
{
    // Editor basics
    "editor.tabSize": 4,
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    
    // TypeScript
    "typescript.preferences.importModuleSpecifier": "relative",
    "typescript.suggest.autoImports": true,
    
    // Svelte
    "svelte.enable-ts-plugin": true,
    
    // File associations
    "files.associations": {
        "*.svelte": "svelte"
    },
    
    // Exclude from search
    "search.exclude": {
        "**/node_modules": true,
        "**/dist": true,
        "**/.svelte-kit": true
    }
}
```

---

## 3.3 Essential Extensions

Install these VS Code extensions:

### Must-Have

| Extension | Purpose |
|-----------|---------|
| **Svelte for VS Code** | Svelte language support |
| **Tailwind CSS IntelliSense** | Tailwind autocomplete |
| **Prettier** | Code formatting |
| **ESLint** | Code linting |
| **Error Lens** | Inline error display |

### Recommended

| Extension | Purpose |
|-----------|---------|
| **GitLens** | Git blame and history |
| **SQLite Viewer** | View .db files |
| **Thunder Client** | API testing |
| **Todo Tree** | Track TODOs |

### Installation via CLI

```bash
# Install all at once
code --install-extension svelte.svelte-vscode
code --install-extension bradlc.vscode-tailwindcss
code --install-extension esbenp.prettier-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension usernamehw.errorlens
code --install-extension eamodio.gitlens
code --install-extension qwtel.sqlite-viewer
```

---

## 3.4 Git Configuration

Version control is essential. Let's set it up properly.

### Initial Configuration

```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Better defaults
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global core.autocrlf input  # Linux/Mac
```

### SSH Key Setup (for GitHub)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your@email.com"

# Start SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Paste this in GitHub → Settings → SSH Keys
```

### Project .gitignore

Create `.gitignore`:

```gitignore
# Dependencies
node_modules/
.pnpm-store/

# Build outputs
.svelte-kit/
build/
dist/

# Environment
.env
.env.local
.env.*.local

# Databases (optional: you might want to track content.db)
data/*.db
data/*.db-wal
data/*.db-shm

# Editor
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
```

---

## 3.5 Project Initialization

Let's create our project from scratch.

### Create Project Directory

```bash
mkdir afidna
cd afidna
```

### Initialize with Bun + SvelteKit

```bash
# Create SvelteKit project
bun create svelte@latest .

# When prompted, choose:
# - Skeleton project
# - TypeScript
# - ESLint: Yes
# - Prettier: Yes
# - Playwright: No (we'll add later)
# - Vitest: No (we'll use Bun's test runner)
```

### Install Dependencies

```bash
# Core dependencies (Bun Native - no external SQLite/bcrypt needed!)
bun add drizzle-orm

# Development dependencies
bun add -d drizzle-kit @types/bun

# UI dependencies
bun add -d tailwindcss @tailwindcss/vite daisyui
```

> **Note**: We use `bun:sqlite` (built-in) instead of `better-sqlite3`,
> and `Bun.password` instead of `bcrypt` for 25x faster hashing!

### SvelteKit Configuration

Update `svelte.config.js`:

```javascript
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    preprocess: vitePreprocess(),
    kit: {
        adapter: adapter(),
        alias: {
            $components: 'src/lib/components',
            $server: 'src/lib/server'
        }
    }
};

export default config;
```

### Tailwind Setup

Create `src/app.css`:

```css
@import 'tailwindcss';
@plugin 'daisyui';

/* RTL Support */
[dir="rtl"] {
    text-align: right;
}

/* Custom utilities */
@layer utilities {
    .card-hover {
        @apply transition-transform hover:scale-[1.02];
    }
}
```

Update `vite.config.ts`:

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [
        tailwindcss(),
        sveltekit()
    ],
    server: {
        fs: {
            allow: ['.']  // للسماح بقراءة ملفات .db
        }
    },
    optimizeDeps: {
        exclude: ['bun:sqlite']  // منع Vite من محاولة حزم المكتبة الأصلية
    },
    build: {
        rollupOptions: {
            external: ['bun:sqlite']  // نفس الشيء عند البناء
        }
    }
});
```

---

## 3.6 Directory Structure Best Practices

Let's organize our project for maintainability.

### The Complete Structure

```
afidna/
├── src/
│   ├── lib/                      # Shared code
│   │   ├── components/           # Svelte components
│   │   │   ├── Navbar.svelte
│   │   │   ├── Footer.svelte
│   │   │   ├── VideoPlayer.svelte
│   │   │   └── Quiz.svelte
│   │   ├── server/               # Server-only code
│   │   │   ├── auth.ts           # Authentication logic
│   │   │   └── db/
│   │   │       ├── index.ts      # Database connections
│   │   │       ├── schema.ts     # users.db schema
│   │   │       └── schema-content.ts
│   │   ├── stores/               # Svelte stores
│   │   │   └── user.ts
│   │   ├── utils/                # Utility functions
│   │   │   └── format.ts
│   │   └── theme.ts              # Theme configuration
│   │
│   ├── routes/                   # SvelteKit routes
│   │   ├── +layout.svelte        # Root layout
│   │   ├── +layout.server.ts     # Layout data
│   │   ├── +page.svelte          # Homepage
│   │   ├── +page.server.ts
│   │   ├── tracks/               # /tracks routes
│   │   ├── lessons/              # /lessons routes
│   │   ├── search/               # /search route
│   │   ├── auth/                 # /auth routes
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   └── logout/
│   │   ├── admin/                # /admin routes
│   │   │   ├── +page.svelte
│   │   │   ├── lessons/
│   │   │   ├── videos/
│   │   │   └── series/
│   │   └── api/                  # API routes
│   │       └── progress/
│   │
│   ├── hooks.server.ts           # Server hooks (middleware)
│   ├── app.html                  # HTML template
│   ├── app.css                   # Global styles
│   └── app.d.ts                  # Type declarations
│
├── scripts/                      # Management scripts
│   ├── setup-db.ts               # Create users.db
│   ├── setup-content.ts          # Create content.db
│   └── seed-content.ts           # Import content
│
├── data/                         # Database files
│   ├── users.db
│   └── content.db
│
├── raw_content/                  # Content source files
│   └── content.json
│
├── static/                       # Static assets
│   ├── favicon.png
│   └── images/
│
├── book/                         # This book!
│
├── .gitignore
├── package.json
├── svelte.config.js
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### Directory Purposes

| Directory | Purpose | Access |
|-----------|---------|--------|
| `src/lib/components/` | Reusable UI components | Client + Server |
| `src/lib/server/` | Server-only code | Server only |
| `src/lib/stores/` | Reactive state | Client only |
| `src/routes/` | Pages and API | Both |
| `scripts/` | CLI utilities | Server only |
| `data/` | Database files | Server only |
| `static/` | Static files | Public |

### Creating the Structure

```bash
# Create all directories
mkdir -p src/lib/{components,server/db,stores,utils}
mkdir -p src/routes/{tracks,lessons,search,auth/{login,register,logout}}
mkdir -p src/routes/admin/{lessons,videos,series}
mkdir -p src/routes/api/progress
mkdir -p scripts
mkdir -p data
mkdir -p raw_content
mkdir -p static/images
```

---

## Verification Checklist

Before moving on, verify your setup:

```bash
# Check Bun
bun --version    # Should be 1.x.x

# Check project runs
bun run dev      # Should start on localhost:5173

# Check TypeScript
bun run check    # Should pass

# Check Git
git status       # Should show your project
```

### Expected Output

When you run `bun run dev`, you should see:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## Summary

In this chapter, we set up:

- ✅ Bun runtime
- ✅ VS Code with essential extensions
- ✅ Git with proper configuration
- ✅ SvelteKit project
- ✅ Tailwind CSS + DaisyUI
- ✅ Organized directory structure

Our development environment is now ready. In the next part, we'll start building the backend — beginning with database design.

---

> **Next Chapter**: [Part II → Chapter 4: Database Design with SQLite](../part-2/chapter-04-database.md)

---

## Quick Reference

### Common Commands

```bash
# Start development server
bun run dev

# Type checking
bun run check

# Format code
bun run format

# Build for production
bun run build

# Preview production build
bun run preview
```

### Troubleshooting

**Problem**: `command not found: bun`
**Solution**: Restart your terminal or run `source ~/.bashrc`

**Problem**: `Port 5173 already in use`
**Solution**: Kill the process or use `bun run dev -- --port 3000`

**Problem**: TypeScript errors in editor
**Solution**: Restart TypeScript server (Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server")
