# Chapter 1: Introduction

---

## 1.1 What We're Building

Welcome to this comprehensive guide on building a modern educational platform from scratch. Throughout this book, we'll create **Afidna** — a fully-featured learning management system (LMS) designed for Islamic scholarly content.

By the end of this journey, you'll have built:

- **A content delivery system** with hierarchical organization (Tracks → Series → Lessons → Videos)
- **User authentication** with secure session management
- **Progress tracking** that saves watch time and quiz scores
- **An interactive quiz system** with instant feedback
- **A video player** integrated with YouTube's API
- **An admin panel** for content management
- **A global search** across all content
- **A responsive UI** supporting both LTR and RTL languages

This isn't a toy project or a simple tutorial app. We're building production-ready software that can serve thousands of users.

---

## 1.2 Why This Tech Stack?

### The Traditional Approach (and Its Problems)

Many educational platforms are built with:
- **Python/Django** or **Node/Express** for the backend
- **React** or **Vue** for the frontend
- **PostgreSQL** or **MySQL** for the database
- **Redis** for sessions
- **Nginx** for reverse proxy

This stack works, but it comes with complexity:
- Multiple services to manage
- High memory footprint
- Complex deployment
- Expensive hosting

### Our Modern Approach

We're taking a different path — the **"Compact Monolith"** philosophy:

| Component | Our Choice | Why |
|-----------|------------|-----|
| **Runtime** | Bun | 4x faster than Node.js, built-in bundler, native TypeScript |
| **Framework** | SvelteKit | SSR + SPA in one, excellent DX, small bundle size |
| **Database** | SQLite | Zero configuration, single file, surprisingly capable |
| **ORM** | Drizzle | Type-safe, lightweight, great SQLite support |
| **UI** | DaisyUI + Tailwind | Beautiful components, rapid development |
| **Auth** | Session-based | Simple, secure, no JWT complexity |

### The Result

- **Single process** to deploy
- **< 100MB RAM** in production
- **Sub-millisecond** database queries
- **$5/month** VPS is more than enough
- **Full-stack TypeScript** — same language everywhere

---

## 1.3 Prerequisites

Before diving in, make sure you have:

### Technical Knowledge
- **JavaScript/TypeScript**: Comfortable with modern ES6+ syntax
- **HTML/CSS**: Basic understanding of web markup
- **Command Line**: Comfortable with terminal basics
- **Git**: Basic version control knowledge

### Not Required (We'll Cover These)
- Svelte/SvelteKit experience
- SQLite knowledge
- Backend development experience
- DevOps skills

### Software Requirements
- **Operating System**: Linux, macOS, or Windows (WSL recommended)
- **Node.js**: Version 18+ (for some tooling)
- **Bun**: We'll install this together
- **Code Editor**: VS Code or Cursor recommended
- **Git**: For version control

---

## 1.4 Project Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Client (Browser)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Homepage   │  │   Lessons   │  │    Admin    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/HTTPS
┌─────────────────────────┴───────────────────────────────┐
│                    SvelteKit Server                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │    Pages    │  │     API     │  │    Auth     │     │
│  │   (SSR)     │  │  Endpoints  │  │  Middleware │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                          │                               │
│  ┌───────────────────────┴────────────────────────┐    │
│  │                 Drizzle ORM                     │    │
│  └───────────────────────┬────────────────────────┘    │
└──────────────────────────┼──────────────────────────────┘
                           │
      ┌────────────────────┴────────────────────┐
      │                                          │
┌─────┴─────┐                            ┌──────┴──────┐
│ users.db  │                            │ content.db  │
│ (R/W)     │                            │ (Read-Only) │
│           │                            │             │
│ • users   │                            │ • tracks    │
│ • sessions│                            │ • series    │
│ • progress│                            │ • lessons   │
└───────────┘                            │ • videos    │
                                         └─────────────┘
```

### Key Design Decisions

1. **Dual Database Strategy**: Separate user data from content
2. **Hierarchical Content**: Tracks → Series → Lessons → Videos
3. **Human-First Editing**: Protect manual edits from automated imports
4. **Progressive Enhancement**: Works without JavaScript, better with it
5. **Mobile-First Design**: Responsive from the start

---

## 1.5 Book Structure

This book is organized into **10 parts**:

### Part I: Foundation & Planning (Chapters 1-3)
Setting up your environment and understanding the architecture.

### Part II: Backend Fundamentals (Chapters 4-7)
Database design, ORM setup, authentication, and API development.

### Part III: Frontend Development (Chapters 8-11)
SvelteKit basics, UI components, and building core pages.

### Part IV: Advanced Features (Chapters 12-15)
Video player, quiz system, progress tracking, and search.

### Part V: Admin Panel (Chapters 16-18)
Building a complete content management interface.

### Part VI: Content Pipeline (Chapters 19-20)
Automated content import and media management.

### Part VII: Testing & Quality (Chapters 21-22)
Testing strategies and code quality tools.

### Part VIII: Deployment (Chapters 23-26)
Production builds, server setup, and monitoring.

### Part IX: Scaling & Optimization (Chapters 27-28)
Performance tuning and growth strategies.

### Part X: Appendices
Reference materials and troubleshooting guides.

---

## How to Use This Book

### If You're Following Along
1. **Type the code yourself** — don't just copy-paste
2. **Run the code after each section** — see it work
3. **Experiment** — break things, fix them
4. **Take notes** — document your learnings

### If You're Using This as Reference
- Each chapter is self-contained
- Code examples are complete and runnable
- The appendices have quick reference guides

### Code Repository
All code from this book is available at:
```
https://github.com/salahAit/afidna-Sveltekit
```

You can clone it to compare with your work or use it as a starting point.

---

## Let's Begin

In the next chapter, we'll dive deep into architecture design — understanding why we make certain decisions and how they impact our application's future.

Get your development environment ready. We're about to build something amazing.

---

> **Next Chapter**: [Chapter 2: Architecture Design](./chapter-02-architecture.md)
