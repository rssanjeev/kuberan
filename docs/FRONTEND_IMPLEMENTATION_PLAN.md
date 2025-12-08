# Frontend Implementation Plan - Kuberan Stock Tracker

**Last Updated:** December 5, 2025  
**Status:** 🚀 Ready to Begin  
**Framework:** Flutter (Web, iOS, Android)  
**Design Reference:** Budget App (https://github.com/theReynald/Budget-App)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Phase-by-Phase Implementation](#phase-by-phase-implementation)
4. [How to Test Each Phase](#how-to-test-each-phase)
5. [Project Structure](#project-structure)
6. [Troubleshooting](#troubleshooting)

---

## Overview

### What We're Building

A Flutter web app that displays your stock tracker data with a clean, card-based layout inspired by the Budget App. You'll be able to:

- ✅ See enrichment progress (12,140 tickers, 41.7% complete)
- ✅ View system status (backend health, MongoDB connection)
- ✅ Search for stocks
- ✅ Navigate between different pages (Home, Stocks, Financier)

### Why This Approach?

**Backend-First Strategy:** Your backend has 67+ working endpoints with real data. The frontend just needs to **display** this data beautifully.

**Design Pattern:** We're copying the Budget App's clean layout:
- Stat cards at the top
- Collapsible status panel
- Form in the middle
- Data table at the bottom

**Beginner-Friendly:** Every phase has:
- Clear goal (what you'll see)
- Exact steps (what I'll do)
- Test instructions (how you verify it works)
- Checkpoint approval (you decide if we continue)

---

## Design Philosophy

### Copied from Budget App

We're **NOT** reinventing the wheel. We're taking proven patterns:

| Budget App Feature | Kuberan Equivalent | Why It Works |
|-------------------|-------------------|--------------|
| **StatCard component** | Shows Starting/Income/Expenses | **Clean visual hierarchy** - Numbers stand out |
| **Collapsible TipOfDay** | System status panel | **Progressive disclosure** - Hide details until needed |
| **Form + Table layout** | Search + Results | **Familiar pattern** - Users know where to look |
| **Color coding** | Green (enriched) / Red (remaining) | **Instant understanding** - No reading required |
| **Responsive grid** | 3-column cards → mobile stack | **Works everywhere** - Desktop and phone |

### Flutter vs React Translation

| React Pattern | Flutter Equivalent | Example |
|--------------|-------------------|---------|
| `<StatCard>` component | `StatCard` widget | Reusable card showing one stat |
| `useState()` hook | `StatefulWidget` | Tracks if panel is expanded |
| `useMemo()` | `computed` property | Calculates percentage |
| Tailwind classes | Material Design | `Card`, `Container`, `Text` |
| `fetch()` API call | `http.get()` | Calls backend |

**Don't worry about the differences!** I'll handle all the Flutter-specific code. You just verify it looks right in your browser.

---

## Phase-by-Phase Implementation

### ✅ Phase 0: Setup (30 minutes) - FIRST STEP

**Goal:** Get Flutter installed and create project structure

#### What I'll Do:
1. Check if Flutter is installed (`flutter --version`)
2. If not installed, provide install command for macOS
3. Run `flutter create kuberan_app` in `frontend/` directory
4. Add required dependencies to `pubspec.yaml`:
   - `http` - Backend API calls
   - `provider` - State management (like React context)
   - `go_router` - Page navigation

#### What You'll Do:
```bash
# If Flutter not installed (I'll detect this)
# Install Flutter (5 minutes)
brew install --cask flutter

# Create project (I'll run this)
cd frontend
flutter create kuberan_app

# Install dependencies (I'll run this)
flutter pub get

# Verify setup
flutter doctor
```

#### What You'll See:
```
✅ Flutter installed
✅ Chrome available for web
✅ Project created
✅ Dependencies installed
```

#### Checkpoint:
- ✅ Run `flutter doctor` - Should show green checkmarks for Chrome
- ✅ Tell me: "Setup complete, continue to Phase 1"

---

### 🎯 Phase 1: "Hello World" Layout (1 hour)

**Goal:** See the Budget App layout with Kuberan branding

#### What I'll Do:

**Files Created (3 files):**
1. `lib/main.dart` - App entry point
2. `lib/screens/home_screen.dart` - Main dashboard
3. `lib/widgets/stat_card.dart` - Reusable stat display card

**Code Structure:**
```
main.dart
  → MaterialApp (Flutter's root)
    → home_screen.dart
      → AppBar ("Kuberan Stock Tracker")
      → Column (vertical layout)
        ├── StatusPanel (collapsible)
        ├── Row (3 StatCards)
        │   ├── StatCard("Total Tickers", "12,140")
        │   ├── StatCard("Enriched", "5,063")
        │   └── StatCard("Remaining", "6,839")
        └── Center("Progress: 41.7%")
```

**UI Design (Exact Layout):**
```
┌─────────────────────────────────────────────┐
│ 📊 Kuberan Stock Tracker           [=]      │ ← AppBar
├─────────────────────────────────────────────┤
│ 🟢 System Status              [Show ▼]      │ ← Collapsible
│ Backend: Connected | MongoDB: Healthy       │
├─────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│ │ TOTAL   │ │ENRICHED │ │REMAINING│        │ ← 3 Cards
│ │ TICKERS │ │ TICKERS │ │ TICKERS │        │
│ │ 12,140  │ │  5,063  │ │  6,839  │        │
│ │         │ │  41.7%  │ │  56.2%  │        │
│ └─────────┘ └─────────┘ └─────────┘        │
├─────────────────────────────────────────────┤
│          📈 Progress: 41.7%                 │ ← Big stat
└─────────────────────────────────────────────┘
```

**Color Scheme (Budget App Colors):**
- Primary: Blue (`#3B82F6`)
- Accent: Indigo (`#6366F1`)
- Success: Green (`#10B981`)
- Warning: Red (`#EF4444`)
- Background: White (`#FFFFFF`)
- Cards: Light gray border (`#E5E7EB`)

#### What You'll Do:
```bash
cd frontend/kuberan_app
flutter run -d chrome
```

#### What You'll See:
1. **Chrome browser opens automatically**
2. **"Kuberan Stock Tracker"** in blue at the top
3. **3 cards side by side** with numbers (hardcoded for now)
4. **Status panel** you can click to expand/collapse
5. **Big percentage** in the center

#### Checkpoint:
Take a screenshot or look at the browser and tell me:
- ✅ "Layout looks good, continue"
- 🔄 "Change card colors to [specify]"
- ❌ "Cards too small, make them bigger"

**WAIT FOR YOUR APPROVAL BEFORE CONTINUING**

---

### 🔌 Phase 2: Backend Connection (1 hour)

**Goal:** Click button → see REAL data from MongoDB

#### What I'll Do:

**Files Created (2 files):**
1. `lib/services/api_service.dart` - Backend communication
2. `lib/models/metadata_stats.dart` - Data structure

**New Features:**
- "Refresh Stats" button
- Loading spinner (while fetching data)
- Error message (if backend is down)
- Auto-refresh every 30 seconds

**Code Flow:**
```
User clicks "Refresh Stats"
  ↓
api_service.dart calls:
  → GET http://localhost:8000/system/metadata/stats
  ↓
Parse JSON response:
  {
    "total": 12140,
    "enriched": 5063,
    "remaining": 6839,
    "percentage": 41.7
  }
  ↓
Update UI:
  StatCard widgets show REAL numbers
```

**API Integration Pattern:**
```dart
// This is what I'll write (you don't need to)
class ApiService {
  Future<MetadataStats> getStats() async {
    final response = await http.get(
      Uri.parse('http://localhost:8000/system/metadata/stats')
    );
    return MetadataStats.fromJson(response.body);
  }
}
```

#### What You'll Do:
```bash
# Make sure backend is running
docker-compose ps  # Should show backend running

# Run Flutter app
cd frontend/kuberan_app
flutter run -d chrome

# In the browser:
# 1. Click "Refresh Stats" button
# 2. Watch spinner appear
# 3. See numbers update
```

#### What You'll See:
1. **Before click:** Cards show "Loading..."
2. **Click "Refresh Stats"** → Spinner appears for 1-2 seconds
3. **After load:** Cards show real numbers from MongoDB:
   - Total Tickers: 12,140
   - Enriched: 5,063 (41.7%)
   - Remaining: 6,839 (58.3%)

**If Backend Is Down:**
```
❌ Error: Cannot connect to backend
   Make sure Docker is running:
   docker-compose up -d
```

#### Checkpoint:
Verify the data:
- ✅ Numbers match what you see in backend logs?
- ✅ Click "Refresh Stats" again - numbers update?
- ✅ Spinner shows while loading?
- ✅ Tell me: "Backend connection works, continue"

**WAIT FOR YOUR APPROVAL BEFORE CONTINUING**

---

### 🧭 Phase 3: Navigation (1 hour)

**Goal:** Multiple pages with side menu (like Budget App had top sections)

#### What I'll Do:

**Files Created (4 files):**
1. `lib/routes/app_router.dart` - Page routing configuration
2. `lib/screens/stocks_screen.dart` - Stock list page
3. `lib/screens/financier_screen.dart` - Transaction page
4. `lib/widgets/app_drawer.dart` - Sidebar menu

**Navigation Structure:**
```
Side Menu (Drawer)
├── 🏠 Home → home_screen.dart (metadata stats)
├── 📈 Stocks → stocks_screen.dart (ticker list)
├── 💰 Financier → financier_screen.dart (transactions)
└── ⚙️ Settings → settings_screen.dart (future)
```

**UI Layout:**
```
┌──────┬──────────────────────────────────┐
│ 🏠   │ Kuberan Stock Tracker       [=]  │
│ Home │                                  │
│──────│  [Your Phase 1 & 2 UI here]     │
│ 📈   │                                  │
│Stock │                                  │
│──────│                                  │
│ 💰   │                                  │
│Finan │                                  │
│──────│                                  │
│ ⚙️   │                                  │
│ Set  │                                  │
└──────┴──────────────────────────────────┘
  ↑ Click to switch pages
```

**How Navigation Works:**
```dart
// When you click "Stocks" in menu:
Navigator.push(
  context,
  MaterialRoute(builder: (context) => StocksScreen())
);

// Page changes → You see new screen
// Browser URL updates: localhost:5173/#/stocks
```

#### What You'll Do:
```bash
# Still running from Phase 2
# Flutter hot reload happens automatically

# In the browser:
# 1. Click hamburger menu (≡) at top-left
# 2. Click "Stocks" → Page changes
# 3. Click "Home" → Back to dashboard
# 4. Click "Financier" → Transaction page
```

#### What You'll See:
1. **Home Page:** Metadata stats (Phase 1 & 2 combined)
2. **Stocks Page:** "Stock list coming soon..." (placeholder for now)
3. **Financier Page:** "Transactions coming soon..." (placeholder)
4. **Side menu:** Slides out when you click ≡
5. **Browser back button:** Works! (goes to previous page)

#### Checkpoint:
Test navigation:
- ✅ Click through all menu items - pages change?
- ✅ Browser back button works?
- ✅ URL updates in address bar?
- ✅ Tell me: "Navigation works, continue to Phase 4"

**WAIT FOR YOUR APPROVAL BEFORE CONTINUING**

---

### 📊 Phase 4: Stock List Page (2 hours)

**Goal:** Show table of enriched stocks (like Budget App's transaction table)

#### What I'll Do:

**Files Created (3 files):**
1. `lib/services/stock_service.dart` - Fetch ticker data
2. `lib/models/ticker_info.dart` - Stock data structure
3. `lib/widgets/ticker_table.dart` - Data table component

**API Call:**
```
GET /system/metadata/tickers?limit=50&enrichment_status=foundation
```

**Table Design:**
```
┌────────┬──────────────────┬────────────┬─────────────┐
│ Ticker │ Company Name     │ Sector     │ Market Cap  │
├────────┼──────────────────┼────────────┼─────────────┤
│ AAPL   │ Apple Inc.       │ Technology │ $2.77T      │
│ MSFT   │ Microsoft Corp   │ Technology │ $2.45T      │
│ GOOGL  │ Alphabet Inc.    │ Technology │ $1.68T      │
│ AMZN   │ Amazon.com Inc.  │ Consumer   │ $1.52T      │
│ ...    │ ...              │ ...        │ ...         │
└────────┴──────────────────┴────────────┴─────────────┘
[Previous] Page 1 of 100 [Next]
```

**Features:**
- Pagination (50 rows per page)
- Click row → See full ticker details
- Search box at top
- Sort by column (click header)
- Loading skeleton (while fetching)

#### What You'll Do:
```bash
# Still running, navigate to Stocks page
# Click "Stocks" in side menu

# Test features:
# 1. Type "AAPL" in search box
# 2. Click "Sector" column header to sort
# 3. Click "Next" to see page 2
# 4. Click a row to see details
```

#### What You'll See:
1. **50 stocks** in a clean table
2. **Search works:** Type "AAPL" → only Apple shows
3. **Sort works:** Click "Market Cap" → Largest first
4. **Pagination:** Click "Next" → See more tickers
5. **Click row:** Opens detail panel (bottom sheet)

#### Checkpoint:
Test the table:
- ✅ See 50 rows?
- ✅ Search filters correctly?
- ✅ Can sort by clicking headers?
- ✅ Pagination works?
- ✅ Tell me: "Stock table works, continue to Phase 5"

**WAIT FOR YOUR APPROVAL BEFORE CONTINUING**

---

### 💰 Phase 5: Financier Page (2 hours)

**Goal:** Upload PDF and see transactions (like Budget App's form)

#### What I'll Do:

**Files Created (4 files):**
1. `lib/services/financier_service.dart` - Upload PDFs, fetch transactions
2. `lib/models/transaction.dart` - Transaction data structure
3. `lib/widgets/pdf_upload_widget.dart` - Drag-and-drop upload
4. `lib/widgets/transaction_table.dart` - Transaction list

**Features:**
- Drag-and-drop PDF upload (like Budget App's form but for files)
- Upload progress bar
- Transaction table (matches Budget App exactly)
- Category pie chart
- Monthly spending summary

**Upload Flow:**
```
User drags PDF file
  ↓
POST /financier/upload
  → File uploads with progress bar
  ↓
Parse transactions
  ↓
Show table:
  [Date] [Merchant] [Amount] [Category]
```

#### What You'll Do:
```bash
# Navigate to Financier page
# Click "Financier" in side menu

# Test upload:
# 1. Drag a PDF statement onto the upload box
# 2. Watch progress bar (0% → 100%)
# 3. See transactions appear in table
```

#### What You'll See:
1. **Upload box:** "Drag PDF here or click to browse"
2. **Drag PDF:** Box highlights blue
3. **Upload:** Progress bar shows 0% → 100%
4. **Success:** "✓ 45 transactions processed"
5. **Table:** All transactions listed
6. **Chart:** Pie chart showing spending by category

#### Checkpoint:
Test file upload:
- ✅ Can drag-and-drop PDF?
- ✅ Progress bar shows?
- ✅ Transactions appear after upload?
- ✅ Can click transaction to edit category?
- ✅ Tell me: "Financier works, continue to Phase 6"

**WAIT FOR YOUR APPROVAL BEFORE CONTINUING**

---

### 🎨 Phase 6: Polish & Mobile (1 hour)

**Goal:** Make it look professional and work on mobile

#### What I'll Do:

**Improvements:**
1. **Responsive Design:**
   - Desktop: 3 cards side-by-side
   - Tablet: 2 cards per row
   - Mobile: 1 card per row (stacked)

2. **Animations:**
   - Card hover effect (shadow grows)
   - Page transitions (slide in/out)
   - Loading skeletons (shimmer effect)

3. **Dark Mode:**
   - Toggle switch in settings
   - All cards adapt to dark theme

4. **Accessibility:**
   - Screen reader support
   - Keyboard navigation
   - High contrast mode

#### What You'll Do:
```bash
# Test responsive design:
# 1. Resize browser window → Cards reorganize
# 2. Open on phone: flutter run -d [phone]
# 3. Toggle dark mode in settings
```

#### What You'll See:
1. **Desktop:** 3 cards wide, everything spacious
2. **Tablet:** 2 cards wide, still readable
3. **Mobile:** 1 card wide, stack vertically
4. **Dark mode:** Black background, white text
5. **Smooth animations:** Cards slide in when page loads

#### Checkpoint:
Test on different sizes:
- ✅ Desktop looks good?
- ✅ Mobile usable?
- ✅ Dark mode works?
- ✅ Tell me: "Polish complete, frontend done!"

**FINAL PHASE COMPLETE! 🎉**

---

## How to Test Each Phase

### Daily Testing Routine

**Morning (Check Progress):**
```bash
# See enrichment progress (backend)
curl http://localhost:8000/system/metadata/stats | jq

# Run frontend
cd frontend/kuberan_app
flutter run -d chrome
```

**After I Make Changes:**
```bash
# Flutter hot reload happens automatically
# Just save the file → UI updates instantly

# If something breaks:
flutter clean
flutter pub get
flutter run -d chrome
```

**Before Approving Phase:**
1. ✅ Click every button
2. ✅ Test on different browser sizes
3. ✅ Check console for errors (F12 → Console tab)
4. ✅ Verify data matches backend
5. ✅ Take screenshots if needed

### Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Cannot connect to backend" | `docker-compose up -d` |
| "Port 5173 already in use" | `killall -9 flutter` then retry |
| "Hot reload not working" | Press `R` in terminal |
| "White screen" | Check console (F12) for errors |
| "Data not updating" | Clear browser cache (Cmd+Shift+R) |

---

## Project Structure

### Final Directory Tree
```
frontend/kuberan_app/
├── lib/
│   ├── main.dart                    # Entry point
│   ├── routes/
│   │   └── app_router.dart          # Navigation config
│   ├── screens/
│   │   ├── home_screen.dart         # Dashboard (Phase 1-2)
│   │   ├── stocks_screen.dart       # Stock list (Phase 4)
│   │   ├── financier_screen.dart    # Transactions (Phase 5)
│   │   └── settings_screen.dart     # Settings (Phase 6)
│   ├── widgets/
│   │   ├── stat_card.dart           # Reusable stat card
│   │   ├── app_drawer.dart          # Side menu
│   │   ├── ticker_table.dart        # Stock table
│   │   ├── transaction_table.dart   # Transaction table
│   │   └── pdf_upload_widget.dart   # File upload
│   ├── services/
│   │   ├── api_service.dart         # Base HTTP client
│   │   ├── stock_service.dart       # Stock API calls
│   │   └── financier_service.dart   # Financier API calls
│   ├── models/
│   │   ├── metadata_stats.dart      # System stats
│   │   ├── ticker_info.dart         # Stock data
│   │   └── transaction.dart         # Transaction data
│   └── utils/
│       ├── constants.dart           # Colors, URLs
│       └── formatters.dart          # Number formatting
├── pubspec.yaml                     # Dependencies
└── README.md                        # Setup instructions
```

### File Purpose (Simple Explanation)

| File | What It Does | Like in Budget App |
|------|--------------|-------------------|
| `main.dart` | App starting point | `App.tsx` |
| `home_screen.dart` | Dashboard with stats | Main `App.tsx` content |
| `stat_card.dart` | One stat display | `StatCard` component |
| `api_service.dart` | Calls backend APIs | `fetch()` calls |
| `app_drawer.dart` | Side menu | Budget App didn't have this |
| `ticker_table.dart` | Stock list table | Transaction table |

---

## Troubleshooting

### "I don't see any changes"

**Try these in order:**
1. Press `R` in terminal (manual hot reload)
2. Press `Shift+R` (full restart)
3. Stop app (Ctrl+C) and `flutter run -d chrome` again
4. Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### "Backend connection failed"

**Check backend is running:**
```bash
docker-compose ps              # Should show "Up"
curl http://localhost:8000/   # Should return API info
```

**If backend is down:**
```bash
docker-compose restart backend
docker logs kuberan-backend-1 --tail 50
```

### "Flutter not found"

**Install Flutter (macOS):**
```bash
# Using Homebrew (easiest)
brew install --cask flutter

# Verify installation
flutter doctor

# Accept licenses
flutter doctor --android-licenses  # Press 'y' for all
```

**Linux/Windows:** See https://docs.flutter.dev/get-started/install

### "Chrome not found"

**Flutter can't find Chrome:**
```bash
# Tell Flutter where Chrome is (macOS)
export CHROME_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Add to ~/.zshrc to make permanent
echo 'export CHROME_EXECUTABLE="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"' >> ~/.zshrc
```

### "Port already in use"

**Kill existing Flutter processes:**
```bash
killall -9 flutter dart
lsof -ti:8080 | xargs kill -9  # Kill process on port 8080
```

### "Package not found"

**Reinstall dependencies:**
```bash
cd frontend/kuberan_app
flutter clean
flutter pub get
flutter pub upgrade
```

---

## Timeline & Milestones

### Parallel Work (During 23-Hour Enrichment)

**Today (Dec 5, 7:40 PM - Midnight):**
- ✅ Phase 0: Setup (30 min)
- ✅ Phase 1: Layout (1 hour)
- ✅ Phase 2: Backend Connection (1 hour)
- ✅ Phase 3: Navigation (1 hour)
- Total: **3.5 hours** → Done by 11:10 PM EST

**Tomorrow (Dec 6, Morning):**
- ✅ Phase 4: Stock List (2 hours)
- ✅ Phase 5: Financier Page (2 hours)
- Total: **4 hours** → Done by noon

**Tomorrow (Dec 6, Afternoon):**
- ✅ Phase 6: Polish (1 hour)
- ✅ Testing & Bug Fixes (1 hour)
- Total: **2 hours** → Done by 2 PM

**Backend Enrichment Completes:** Dec 6, ~7 PM EST

**Result:** Frontend 100% done **5 hours before** enrichment finishes! 🎉

---

## Success Criteria

### Phase Completion Checklist

**Phase 1 Complete When:**
- [ ] Flutter app runs in Chrome
- [ ] See 3 stat cards
- [ ] Can expand/collapse status panel
- [ ] Layout matches Budget App structure

**Phase 2 Complete When:**
- [ ] "Refresh Stats" button works
- [ ] Real data from MongoDB displays
- [ ] Loading spinner shows
- [ ] Error message if backend is down

**Phase 3 Complete When:**
- [ ] Side menu opens/closes
- [ ] Can navigate to 3 different pages
- [ ] Browser back button works
- [ ] URL updates in address bar

**Phase 4 Complete When:**
- [ ] See 50 stocks in table
- [ ] Search filters correctly
- [ ] Can sort by column
- [ ] Pagination works

**Phase 5 Complete When:**
- [ ] Can upload PDF
- [ ] Progress bar shows
- [ ] Transactions display in table
- [ ] Pie chart shows spending

**Phase 6 Complete When:**
- [ ] Responsive on desktop/tablet/mobile
- [ ] Dark mode toggles
- [ ] Animations smooth
- [ ] No console errors

---

## Next Steps After Completion

### When Frontend Is Done

**Immediate (Dec 6, 2 PM):**
1. Deploy to GitHub Pages (free hosting)
2. Share URL with friends for feedback
3. Write user guide (screenshots + instructions)

**Short-term (Dec 7-10):**
1. Add more features:
   - Stock price charts (use fl_chart package)
   - Portfolio tracking
   - Alerts/notifications
2. Connect remaining backend endpoints (67 ETF endpoints!)

**Long-term (Dec 11+):**
1. Mobile app (iOS/Android) - same codebase!
2. Desktop app (macOS/Windows) - same codebase!
3. Add authentication (login page)

---

## Getting Help

### If You're Stuck

**Before asking me, try:**
1. Check [Troubleshooting](#troubleshooting) section above
2. Look at Flutter docs: https://docs.flutter.dev
3. Check browser console (F12 → Console tab)
4. Run `flutter doctor -v` for diagnostic info

**When asking me for help, provide:**
1. What phase are you on?
2. What did you try?
3. Error message (copy-paste entire error)
4. Screenshot of what you see

**I will respond with:**
1. Exact command to fix it
2. Explanation of what went wrong
3. How to prevent it next time

---

## Vocabulary (Beginner-Friendly)

**Terms you'll see:**

| Term | Simple Explanation | Example |
|------|-------------------|---------|
| **Widget** | A UI component (like React component) | `StatCard` is a widget |
| **StatefulWidget** | Widget that can change (has data) | Counter that updates |
| **StatelessWidget** | Widget that never changes (just displays) | Text label |
| **Hot Reload** | Update UI without restarting app | Save file → UI updates |
| **Scaffold** | Page template (has AppBar, body, etc.) | Every screen uses this |
| **Provider** | Shares data between widgets | Like React Context |
| **Navigator** | Controls page changes | Click menu → new page |
| **MaterialApp** | Makes app look like Android/iOS | Root of all Flutter apps |

**Don't memorize these!** I'll handle all the Flutter-specific stuff. You just click, drag, and verify it works.

---

## Summary

**What We're Doing:**
- Copying Budget App's clean layout
- Showing your backend data in cards and tables
- Building 6 phases over 2 days
- Testing after each phase

**Your Role:**
- Look at browser
- Click buttons
- Tell me if it looks right
- Approve each phase

**My Role:**
- Write all the code
- Explain every step
- Wait for your approval
- Fix any issues

**Timeline:**
- Start tonight (Phase 0-3)
- Finish tomorrow (Phase 4-6)
- Done before enrichment completes

**Ready?** Tell me: "Start Phase 0 - Setup" and I'll begin! 🚀

---

**Last Updated:** December 5, 2025  
**Next Phase:** Phase 0 - Setup (waiting for approval)
