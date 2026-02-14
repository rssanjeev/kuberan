# Manual Income & Expense Entries

## Overview

This directory contains the `manual_entries.json` file where you can add hardcoded income and expenses that don't come from credit card statements.

**Use Cases:**
- **Recurring Income**: Biweekly paychecks that are always the same amount
- **Adhoc Expenses**: One-time checking account expenses (gym, insurance, utilities, etc.)
- **Income from Checking Account**: Already captured income without re-uploading statements

## File Structure

### manual_entries.json

```json
{
  "recurring_income": {
    "enabled": true,
    "amount": 3140.62,
    "frequency": "biweekly",
    "start_date": "2025-01-03",
    "description": "Payroll",
    "category": "Income"
  },
  "adhoc_expenses": [
    {
      "date": "2025-02-15",
      "description": "Planet Fitness Membership",
      "category": "Health & Pharmacy",
      "amount": 50.00
    },
    {
      "date": "2025-02-20",
      "description": "Car Insurance Payment",
      "category": "Transportation",
      "amount": 150.00
    }
  ]
}
```

## Getting Started

### 1. Create Your File

Copy the example file:
```bash
cd backend/data
cp manual_entries.json.example manual_entries.json
```

### 2. Configure Recurring Income

Edit the `recurring_income` section:

**Fields:**
- **enabled**: Set to `true` to activate recurring income
- **amount**: Your paycheck amount (e.g., 3140.62)
- **frequency**: Choose from:
  - `"biweekly"` - Every 2 weeks (most common)
  - `"weekly"` - Every week
  - `"monthly"` - Once per month
- **start_date**: First paycheck date in YYYY-MM-DD format
- **description**: What to call it (e.g., "Payroll", "Salary")
- **category**: Always `"Income"`

**Example:**
```json
"recurring_income": {
  "enabled": true,
  "amount": 3140.62,
  "frequency": "biweekly",
  "start_date": "2025-01-03",
  "description": "Tech Corp Payroll",
  "category": "Income"
}
```

### 3. Add Adhoc Expenses

Add one-time or irregular expenses to the `adhoc_expenses` array:

**Fields:**
- **date**: Transaction date in YYYY-MM-DD format
- **description**: What you paid for
- **category**: Spending category (must match existing categories)
- **amount**: Dollar amount (positive number)

**Example:**
```json
"adhoc_expenses": [
  {
    "date": "2025-02-01",
    "description": "Planet Fitness Monthly",
    "category": "Health & Pharmacy",
    "amount": 50.00
  },
  {
    "date": "2025-02-15",
    "description": "Progressive Car Insurance",
    "category": "Transportation",
    "amount": 165.00
  },
  {
    "date": "2025-02-28",
    "description": "Electric Bill",
    "category": "Home & Garden",
    "amount": 120.00
  }
]
```

## Available Categories

Your expenses MUST use one of these existing categories:

- **Dining & Drinks**: Restaurants, bars, coffee shops
- **Groceries**: Supermarkets, food shopping
- **Transportation**: Gas, Uber, parking, insurance
- **Shopping**: Retail, Amazon, Target, Costco
- **Entertainment**: Movies, games, streaming
- **Health & Pharmacy**: Gym, CVS, medical
- **Home & Garden**: Home Depot, utilities, furniture
- **Travel**: Hotels, flights, vacation expenses
- **Gas & Auto**: Shell, Exxon, car maintenance
- **Technology**: Electronics, software, gadgets
- **Subscriptions**: Netflix, Spotify, memberships
- **Personal Care**: Haircuts, spa, cosmetics
- **Pet Care**: Vet, pet food, supplies
- **Education**: Books, courses, tuition
- **Gifts & Donations**: Presents, charity
- **Fees & Charges**: Bank fees, ATM charges
- **Miscellaneous**: Other expenses
- **Investments**: Charles Schwab, Webull, etc. (excluded from spending)

**Special Categories (Auto-excluded from spending):**
- **Income**: Paychecks, deposits
- **Zelle Received**: Money received via Zelle
- **Investments**: Investment contributions

## How It Works

### Data Flow

1. **You edit** `manual_entries.json` with your income and expenses
2. **Analytics service** loads the file when calculating spending
3. **Recurring income** is generated for the selected month/year
4. **Adhoc expenses** are filtered by date
5. **Manual entries** are merged with credit card transactions
6. **Category breakdown** shows combined totals
7. **Cash flow** includes manual income in calculations

### Integration Points

Manual entries are automatically included in:
- ✅ Monthly spending summaries
- ✅ Category breakdowns
- ✅ Cash flow calculations (income vs expenses)
- ✅ Comprehensive analytics
- ✅ Financial health indicators
- ❌ Investment analysis (only shows actual investments)

### Example Scenario

**Situation:** 
- You get paid $3,140.62 every 2 weeks
- You pay $50/month for gym from checking account
- You paid $150 for car insurance in February

**Solution:**
```json
{
  "recurring_income": {
    "enabled": true,
    "amount": 3140.62,
    "frequency": "biweekly",
    "start_date": "2025-01-03",
    "description": "Payroll",
    "category": "Income"
  },
  "adhoc_expenses": [
    {
      "date": "2025-02-01",
      "description": "Planet Fitness",
      "category": "Health & Pharmacy",
      "amount": 50.00
    },
    {
      "date": "2025-02-15",
      "description": "Car Insurance",
      "category": "Transportation",
      "amount": 150.00
    }
  ]
}
```

**Result:**
- February 2025 analytics will show:
  - Income: $6,281.24 (2 paychecks × $3,140.62)
  - Health & Pharmacy: +$50 from gym
  - Transportation: +$150 from insurance
  - Spending total includes these adhoc expenses

## Validation

The system will:
- ✅ Continue working if file is missing (just uses credit card data)
- ✅ Log warnings if JSON is malformed
- ✅ Skip invalid dates or amounts
- ✅ Default to empty arrays/disabled if fields missing

## Best Practices

### 1. Start Date Accuracy

Set `start_date` to your actual first paycheck date. The system will calculate all future paychecks from this date.

**Good:**
```json
"start_date": "2025-01-03"  // Your actual first paycheck of 2025
```

**Bad:**
```json
"start_date": "2025-01-01"  // Random date, won't match real paychecks
```

### 2. Keep Descriptions Clear

Use descriptions that will make sense 6 months from now.

**Good:**
```json
"description": "Planet Fitness Monthly Membership"
```

**Bad:**
```json
"description": "Gym"
```

### 3. One Entry Per Transaction

Don't combine multiple expenses into one entry.

**Good:**
```json
[
  {"date": "2025-02-01", "description": "Electric Bill", "amount": 120},
  {"date": "2025-02-01", "description": "Water Bill", "amount": 45}
]
```

**Bad:**
```json
[
  {"date": "2025-02-01", "description": "Utilities", "amount": 165}
]
```

### 4. Update Regularly

Add adhoc expenses as they happen:
- Monthly: Gym, insurance, subscriptions
- Quarterly: Estimated taxes, HOA fees
- Annually: Prime membership, car registration

### 5. Backup Your File

This file is **git-ignored** (for your privacy), so it won't be committed. 

**Backup manually:**
```bash
cp backend/data/manual_entries.json ~/backups/manual_entries_$(date +%Y%m%d).json
```

## Troubleshooting

### "Manual entries not showing up"

**Check:**
1. File exists: `backend/data/manual_entries.json`
2. Valid JSON (use https://jsonlint.com)
3. Date format is YYYY-MM-DD
4. Category matches existing categories exactly
5. Amount is positive number

**Test:**
```bash
# Validate JSON
python3 -m json.tool backend/data/manual_entries.json
```

### "Recurring income not calculated"

**Check:**
1. `"enabled": true` is set
2. `start_date` is valid date
3. `frequency` is "biweekly", "weekly", or "monthly"
4. Selected month/year is after start date

### "Wrong income amount"

**Cause:** Frequency mismatch or wrong start date

**Fix:**
- For biweekly (every 2 weeks), you'll get 2-3 paychecks per month
- For monthly, you'll get 1 paycheck
- Check start_date matches your actual payday

### "Expense in wrong category"

**Cause:** Category name doesn't match exactly (case-sensitive)

**Fix:**
```json
// ❌ Wrong
"category": "health & pharmacy"

// ✅ Correct
"category": "Health & Pharmacy"
```

## Security & Privacy

### Why This File Is Git-Ignored

Your `manual_entries.json` file contains:
- Your exact income amount
- Your spending patterns
- Potentially identifiable transactions

**This is PRIVATE financial data** and should never be committed to git.

### File Location

- ✅ `backend/data/manual_entries.json` - Git-ignored
- ✅ `backend/data/manual_entries.json.example` - Safe template (no real data)

### Sharing This Repo

If you share this codebase:
- ❌ Your `manual_entries.json` won't be included
- ✅ The example file will be included
- ✅ New users start with empty file

## Future Enhancements

Planned features (not yet implemented):

- [ ] Web UI for adding/editing entries
- [ ] Import from CSV
- [ ] Validation API endpoint
- [ ] Calendar view of recurring income
- [ ] Expense templates (common bills)
- [ ] Multiple income sources
- [ ] Annual adjustments (raises)

## Support

Questions? Check the logs:
```bash
docker logs kuberan-backend-1 | grep "manual entries"
```

You'll see:
- "Loaded manual entries" - File loaded successfully
- "Integrated manual entries" - Added to analysis
- "Manual entries file not found" - File missing (not an error)
- "Invalid JSON" - Fix JSON syntax

---

**Last Updated:** December 5, 2025  
**File Version:** 1.0
