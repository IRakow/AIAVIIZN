# 🔥 QUICK START - COPY & PASTE

## STEP 1: SETUP (First time only)
```bash
cd /Users/ianrakow/Desktop/AIVIIZN
chmod +x setup.sh
./setup.sh
```

## STEP 2: PROCESS A PAGE
```bash
./process.sh
```

That's it! The browser will open and process the page.

## 📋 WHAT HAPPENS:
1. **Browser opens** (you'll see it)
2. **Goes to AppFolio page**
3. **Extracts everything**
4. **Creates your template**
5. **Shows next pages to process**

## 🎯 PROCESS SPECIFIC PAGE:
```bash
./process.sh https://celticprop.appfolio.com/reports/rent_roll
```

## ✅ THIS IS REAL CODE
- Real browser (not mock)
- Real extraction (not fake)
- Real templates (not examples)
- Real database (not simulation)

## ⚠️ IF LOGIN REQUIRED:
When the browser opens, if you see a login page:
1. Log in manually
2. Press ENTER in terminal
3. Script continues automatically

## 📊 AFTER EACH PAGE:
- Template created in `/templates/`
- State saved in `/data/`
- Queue updated with new links
- Run again for next page

## 🚀 JUST RUN:
```bash
./process.sh
```
