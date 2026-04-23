# User Hub Documentation (`landing-hub-sidebar.tsx`)

## Overview

The User Hub ("Your Wellnest") is a right-side drawer that personalizes the landing experience using local journey state.

The hub has two major modes:

1. Onboarding mode (new user)
2. Returning user mode (existing journey signals)

---

## 1) Onboarding Mode (New User)

Shown when the user has not completed onboarding (primarily no selected life moment).

### Sections in this mode

- **Step 1 of 2 - Welcome**
  - Intro copy to start setup.
  - Prompts users to set suburb first.

- **Where are you living right now?**
  - Suburb input + `Set suburb` button.
  - Saves suburb to local storage for personalization.

- **Step 2 of 2: Pick a moment**
  - Life moments:
    - `I just arrived`
    - `I'm getting set up`
    - `I'm looking for my people`
  - Each moment includes:
    - `Choose` (sets life moment in local state)
    - `Start with guides` (opens filtered Guides)
    - `Near Me` (opens filtered Near Me)

- **Starter recommendation**
  - Dynamic recommendation based on selected life moment.

- **Privacy note**
  - States that journey data stays on device.

### Onboarding links and destinations

- `I just arrived`
  - Guides: `/guides?category=survive`
  - Near Me: `/near-me?category=health`

- `I'm getting set up`
  - Guides: `/guides?category=setup`
  - Near Me: `/near-me?category=get-around`

- `I'm looking for my people`
  - Guides: `/guides?category=connect`
  - Near Me: `/near-me?category=connect`

---

## 2) Returning User Mode

Shown when local journey signals exist (for example selected life moment, read history, arc progress, or saved places).

### Sections in this mode

- **Welcome back**
  - Personalized reflection summary (suburb, progress, topic focus, mood nudge).

- **How's this week?**
  - Mood chips:
    - `settled`
    - `figuring it out`
    - `overwhelmed`
    - `lonely`
  - Influences reflective copy only (no page navigation).

- **Continue reading**
  - Shows active life moment + suggested next guide.
  - CTA: `Continue`.

- **Your journey**
  - Arc progress cards:
    - `Week 1`
    - `Month 1`
    - `Month 3`
  - Each card links to Guides.

- **Your suburb**
  - Update and save suburb.
  - Shows local context (population for selected suburb).
  - If saved locations exist, shows tags and a `See all` link.

- **Jump to a topic**
  - Expand/collapse topic cards:
    - Food & Eating
    - Getting Around
    - Health & Wellbeing
    - Home & Admin
    - Social & Belonging
  - Each topic links to filtered Guides.

- **Journey receipt controls**
  - Local continuity tools:
    - `Export receipt`
    - `Import receipt`
    - `Preview receipt` (opens modal)
    - `Clear local data`

### Returning user links and destinations

- **Continue reading CTA**
  - Dynamic by active moment:
    - `/guides?category=survive`
    - `/guides?category=setup`
    - `/guides?category=connect`

- **Journey arc cards**
  - `Week 1`, `Month 1`, `Month 3` -> `/guides`

- **Saved locations**
  - `See all` -> `/near-me`

- **Jump to a topic**
  - Food & Eating -> `/guides?category=survive`
  - Getting Around -> `/guides?category=get-around`
  - Health & Wellbeing -> `/guides?category=health`
  - Home & Admin -> `/guides?category=setup`
  - Social & Belonging -> `/guides?category=connect`

---

## Data and behavior notes

- Hub state is local-first and read from landing local storage state.
- Suburb context is fetched from `/api/population?location=<suburb>`.
- Receipt actions support local backup/restore continuity.
