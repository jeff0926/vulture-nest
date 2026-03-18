# 864zeros Factory Inventory

> Generated: 2026-03-18 | Total Extensions: 17

## Executive Summary

This inventory catalogs all harvestable components across the 864zeros extension portfolio. Use this to avoid "Frankenstein" builds by sourcing proven UI patterns and logic bricks from existing stable extensions.

---

## Extension Registry

| ID | Name | Purpose | Brand | UI Type | Status |
|----|------|---------|-------|---------|--------|
| bible-insight | Bible Insight | Bible Study / Sermon Notes | FHG | SidePanel | Stable |
| clipboard | ClipBoard | Clipboard Manager | OIA | SidePanel | Stable |
| tabvault | TabVault | Tab Manager | OIA | SidePanel | Stable |
| signal2noise | Signal2Noise | Task Prioritization | OIA | SidePanel | Stable |
| tuneout2focusin | TuneOut2FocusIn | Background Noise | OIA | SidePanel | Stable |
| time2focus | Time2Focus | Focus Timer | OIA | SidePanel | Stable |
| 864z-chronical | Chronicle | AI Conversation History | 864z | SidePanel | Stable |
| who-is-watching | Who Is Watching | Tracker Detector | OIA | SidePanel | Stable |
| oia-focus-note | OIA Focus Note | Note Taking | OIA | SidePanel | Minimal |
| oia-focus-timer | OIA Focus Timer | Timer | OIA | SidePanel | Minimal |
| oia-focus-wall | OIA Focus Wall | Wallpaper | OIA | SidePanel | Minimal |
| oia-focus-sound | OIA Focus Sound | Sound Player | OIA | SidePanel | Minimal |
| oia-focus-signal | OIA Focus Signal | Notifications | OIA | SidePanel | Minimal |
| 864z-2026-002 | ReadVault (Pocket Alt) | Reader | 864z | SidePanel | Active |
| 864z-2026-003 | InstaRescue | Data Rescue | 864z | Library | Scaffold |
| 864z-2026-004 | PassVault | Password Manager | 864z | SidePanel | Active |
| 864z-2026-005 | ReadFlow | Reader / Kobo Sync | 864z | SidePanel | Active |

---

## Harvestable Features by Category

### PARSERS (Data Import)

| Brick | Source | Formats Supported | Harvest For |
|-------|--------|-------------------|-------------|
| `password-parser.js` | PassVault | Dashlane, LastPass, 1Password, CSV | Any password/credential import |
| `instapaper-parser.js` | ReadFlow | Instapaper CSV | Read-it-later import |
| `pocket-parser.js` | Pocket Alt | Pocket export | Read-it-later import |
| `deep-parser.js` | InstaRescue | Generic CSV | Universal CSV parsing |
| `verse-detector.js` | Bible Insight | Bible references (regex + NLP) | Religious/text apps |

### EXPORTERS (Data Export)

| Brick | Source | Output Format | Harvest For |
|-------|--------|---------------|-------------|
| `epub-builder.js` | ReadFlow | ePub | E-reader export, document generation |
| `recovery-pdf.js` | PassVault | PDF | Recovery documents, reports |
| `pdf-generator.js` | ClipBoard | PDF | Generic PDF generation |
| `qr-generator.js` | ReadFlow | QR Code (SVG) | Wireless transfer, sharing |

### SECURITY

| Brick | Source | Features | Harvest For |
|-------|--------|----------|-------------|
| `crypto-vault.js` | PassVault | AES-GCM encryption, key derivation | Any local-first security |
| `breach-checker.js` | PassVault | HaveIBeenPwned API integration | Password audits |
| `detector.js` | Who Is Watching | Tracker/fingerprint detection | Privacy tools |
| `redactor.js` | ClipBoard | Content redaction | Privacy/security features |

### STORAGE & SYNC

| Brick | Source | Features | Harvest For |
|-------|--------|----------|-------------|
| `db.js` | Multiple | IndexedDB wrapper | Any local storage |
| `backup.js` | ClipBoard | JSON export/import | Data portability |
| `google-drive/` | ClipBoard | OAuth2 + Drive API | Cloud backup |
| `store.js` | Pocket Alt | State management | App state |

### UI SYSTEMS

| Brick | Source | Features | Harvest For |
|-------|--------|----------|-------------|
| `oia-design-system.css` | Multiple | Dark theme, typography, cards, forms | OIA brand apps |
| `aether-ui.css` | ReadFlow | Brand footer, modals, lists | 864zeros brand apps |
| `BRK-PRICING-001.js` | PassVault | Pricing modal controller | Monetization |
| `864z-core.js` | Build Kit | Brand constants, legal URLs | All 864zeros apps |

### AUDIO

| Brick | Source | Features | Harvest For |
|-------|--------|----------|-------------|
| Offscreen audio pattern | TuneOut2FocusIn | MV3 background audio playback | Any audio app |
| Alert sounds | Time2Focus | Chime, bowl, raindrop, bell | Notifications |

---

## UI Component Patterns

### READER UI (Harvest from Pocket Alt / ReadFlow)

| Component | Source | Description |
|-----------|--------|-------------|
| Article Card | Pocket Alt | Favicon + title + domain + reading time |
| Article List | ReadFlow | Scrollable list with folder badges |
| Empty State | ReadFlow | Icon + title + CTA button |
| Search Bar | Both | Input with search icon prefix |

**RECOMMENDATION FOR READFLOW:** Replace the current "vault" icons (lock icon in header/logo) with Reader-appropriate icons (book/article). Harvest the article card pattern from Pocket Alt for consistent reader UX.

### SECURITY UI (Harvest from PassVault)

| Component | Source | Description |
|-----------|--------|-------------|
| Password Card | PassVault | Site favicon + username + strength indicator |
| Audit Modal | PassVault | Statistics grid + breakdown rows + savings banner |
| Import Modal | PassVault | Dropzone + source selection (Dashlane/LastPass/etc) |
| Lock Overlay | PassVault | Full-screen lock with unlock form |

### FOCUS UI (Harvest from Time2Focus / Signal2Noise)

| Component | Source | Description |
|-----------|--------|-------------|
| Preset Buttons | Time2Focus | 2x2 grid of large tap targets |
| Signal Pill | Signal2Noise | Horizontal bar showing priority items |
| Accordion List | Signal2Noise | Collapsible note cards |
| Flash Overlay | Time2Focus | Gentle pulse animation on completion |

### BRAND FOOTER (Universal)

| Component | Source | Description |
|-----------|--------|-------------|
| Brand Footer | aether-ui.css | "864zeros" logo + OIA mission + legal links + Upgrade |
| Pricing Modal | BRK-PRICING-001.js | Free/Pro $12/mo/Lifetime $150 tiers |

---

## Priority Harvest List (ReadFlow Fix)

To fix ReadFlow's "Frankenstein" UI, harvest these components:

1. **Article Card UI** from `864z-2026-002-pocket-alt/sidepanel/`
   - Proper favicon handling
   - Domain extraction
   - Reading time display
   - Folder badge

2. **Empty State** from `864z-2026-002-pocket-alt/sidepanel/`
   - Book/article icon (NOT vault icon)
   - "Your reading list is empty" messaging
   - Import CTA

3. **Reader Icons** - Replace all lock/vault SVGs with:
   - Book icon for logo
   - Article/page icon for list items
   - Download icon for export

4. **Import Modal** - Keep current (already reader-appropriate)

5. **Rescue Audit Modal** - Keep current (already excellent "Aha!" moment)

---

## File Locations

### 864zeros/extensions/
```
Bible-Insight/js/lib/verse-detector.js
clipboard/lib/google-drive/
clipboard/lib/pdf-generator.js
clipboard/lib/backup.js
clipboard/lib/oia-design-system.css
who-is-watching/content/detector.js
```

### vulture-nest/864zeros_engine/builds/
```
864z-2026-002-pocket-alt/lib/pocket-parser.js
864z-2026-002-pocket-alt/sidepanel/  (Reader UI)
864z-2026-003-instarescue/lib/deep-parser.js
864z-2026-004-passvault/lib/password-parser.js
864z-2026-004-passvault/lib/crypto-vault.js
864z-2026-004-passvault/lib/breach-checker.js
864z-2026-004-passvault/lib/recovery-pdf.js
864z-2026-005-readflow/lib/instapaper-parser.js
864z-2026-005-readflow/lib/epub-builder.js
864z-2026-005-readflow/lib/qr-generator.js
864z-2026-005-readflow/lib/article-fetcher.js
```

### vulture-nest/864z-build-kit/
```
lib/864z-core.js
lib/BRK-PRICING-001.js
lib/aether-ui.css
scripts/strike-bridge.js
```

---

## Next Actions

1. **ReadFlow UI Fix**: Harvest article card UI from Pocket Alt, replace vault icons with reader icons
2. **Brick Standardization**: Move all harvestable bricks to `864z-build-kit/lib/`
3. **Strike Bridge Update**: Add all bricks to `strike-bridge.js` scaffold generator
4. **Version Bricks**: Add version numbers and changelog to each brick

---

*Last updated: 2026-03-18*
*Maintained by: 864zeros Build System*
