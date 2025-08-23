# 🔧 DEPENDENCY FIX

The error you're seeing is a common websockets version conflict. Here's how to fix it:

## 🚀 QUICK FIX:

```bash
cd /Users/ianrakow/Desktop/AIVIIZN
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

## 🐍 OR USE VIRTUAL ENVIRONMENT (RECOMMENDED):

```bash
cd /Users/ianrakow/Desktop/AIVIIZN
chmod +x setup.sh run_agent.sh

# This creates a clean environment
./setup.sh

# Then run the agent
./run_agent.sh
```

## 🔧 MANUAL FIX:

```bash
pip3 uninstall -y supabase websockets realtime
pip3 install websockets>=12.0
pip3 install supabase==2.0.2
pip3 install playwright anthropic beautifulsoup4 python-dotenv
python3 -m playwright install
```

## ✅ THEN RUN:

```bash
python3 aiviizn_real_agent.py
```

The virtual environment approach is cleanest and prevents future conflicts!
