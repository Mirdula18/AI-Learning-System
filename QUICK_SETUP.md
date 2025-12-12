# 🚀 Quick Setup Guide - Automatic Resource Generation

## ⚡ 3-Step Setup (Takes 2 minutes!)

### Step 1: Get FREE Gemini API Key

1. Go to: **https://makersuite.google.com/app/apikey**
2. Sign in with Google
3. Click **"Create API Key"**
4. Copy the key (looks like: `AIzaSyD...`)

---

### Step 2: Add API Key to Project

**Open or create**: `adaptlearn/.env`

**Add this line**:
```env
GEMINI_API_KEY=paste_your_actual_key_here
```

**Example**:
```env
GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

### Step 3: Restart Server

```bash
# Stop server (Ctrl+C in terminal)
# Start again
python manage.py runserver
```

---

## ✅ Test It Works!

### Quick Test:

1. **Go to**: http://localhost:8000/register/
2. **Create account** and complete profile
3. **Take assessment**: Enter "Python" → Complete quiz
4. **Click**: "Generate Learning Roadmap"
5. **Watch terminal**: Should see:
   ```
   Starting automatic resource generation...
   Generated 5 resources for Python Basics using Gemini
   Resource generation complete!
   ```
6. **Go to**: http://localhost:8000/roadmap/
7. **Expand a topic** → See auto-generated resources! 🎉

---

## 🎯 What You'll See

### Without API Key:
```
📚 Resources:
  🔗 Search: Python Documentation
  🔗 Search: Python Tutorial Videos
```
*(Fallback mode - search links)*

### With API Key:
```
📚 Resources:
  📄 Official Python Tutorial
     https://docs.python.org/3/tutorial/
     
  🎥 Python for Beginners - Full Course
     https://www.youtube.com/watch?v=...
     
  📰 Real Python - Getting Started Guide
     https://realpython.com/start-here/
```
*(AI-curated real resources!)*

---

## 📝 Alternative: Use .env.example

If `.env` doesn't exist:

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your API key
# Save and restart server
```

---

## 🐛 Troubleshooting

### "Resources not appearing"

**Check 1**: API key in .env file?
```bash
# View .env file
cat adaptlearn/.env

# Should see:
GEMINI_API_KEY=AIzaSy...
```

**Check 2**: Server restarted after adding key?
```bash
# Stop and restart server
python manage.py runserver
```

**Check 3**: Check terminal logs
```
Look for:
✅ "Generated X resources using Gemini"
❌ "No LLM API key found"
```

---

## 🎓 How It Works

```
User generates roadmap
    ↓
System extracts topics (e.g., "Python Basics", "Data Structures")
    ↓
For each topic:
  • Send to Gemini AI: "Find best learning resources for [topic]"
  • AI searches and curates: docs, videos, articles
  • Returns JSON with titles, URLs, descriptions
    ↓
Save all resources to database
    ↓
User sees them on roadmap page immediately!
```

### Magic Files:
- `core/resource_generator.py` - AI integration
- `core/views.py` (line 408) - Triggers auto-generation
- `.env` - Your API key

---

## 💰 Cost

**Google Gemini**:
- ✅ **FREE** for most use cases
- 60 requests/minute free tier
- Perfect for development and small apps

**Anthropic Claude** (optional alternative):
- ⚠️ Paid only (~$0.01 per request)
- Not needed if using Gemini

---

## 🎉 That's It!

**Total time**: 2 minutes
**Total cost**: $0 (free!)
**Result**: Automatic AI-powered resource generation!

No more manual admin work → Resources appear automatically for every topic! 🚀

---

## 📚 Need More Info?

See full documentation: `AUTOMATIC_RESOURCE_GENERATION.md`
