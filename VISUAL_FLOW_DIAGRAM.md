# 🎨 Automatic Resource Generation - Visual Flow Diagram

## 📊 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER JOURNEY                                 │
└─────────────────────────────────────────────────────────────────┘

1. User Registration
   └─> http://localhost:8000/register/
       Create account

2. Assessment
   └─> http://localhost:8000/courses/
       Enter: "Python Programming"
       Complete Quiz

3. Generate Roadmap
   └─> Click "Generate Learning Roadmap"
       │
       ├─> Backend: core/views.py → generate_roadmap()
       │
       ├─> Step 1: Generate Learning Path
       │   └─> core/roadmap_generator.py
       │       Returns: {
       │         learning_path: [
       │           {topic: "Python Basics"},
       │           {topic: "Data Structures"},
       │           ...
       │         ]
       │       }
       │
       ├─> Step 2: 🤖 AUTO-GENERATE RESOURCES (NEW!)
       │   └─> core/resource_generator.py
       │       │
       │       ├─> For each topic in roadmap:
       │       │   │
       │       │   ├─> Check if resources exist
       │       │   │   SELECT * FROM TopicResource
       │       │   │   WHERE topic = "Python Basics"
       │       │   │
       │       │   ├─> If NOT exists:
       │       │   │   │
       │       │   │   ├─> Call LLM API (Gemini/Claude)
       │       │   │   │   POST https://generativelanguage.googleapis.com/
       │       │   │   │   Request: "Find best resources for Python Basics"
       │       │   │   │   │
       │       │   │   │   Response: {
       │       │   │   │     resources: [
       │       │   │   │       {
       │       │   │   │         title: "Official Python Tutorial",
       │       │   │   │         type: "document",
       │       │   │   │         url: "https://docs.python.org/...",
       │       │   │   │         description: "..."
       │       │   │   │       },
       │       │   │   │       ...
       │       │   │   │     ]
       │       │   │   │   }
       │       │   │   │
       │       │   │   └─> Save to Database
       │       │   │       INSERT INTO TopicResource
       │       │   │       (topic, title, description, type, url, order)
       │       │   │       VALUES (...)
       │       │   │
       │       │   └─> If exists: Skip (use cached)
       │       │
       │       └─> Return stats: {
       │           total_topics: 10,
       │           topics_processed: 10,
       │           total_resources_created: 53
       │         }
       │
       └─> Return roadmap with resource stats to frontend

4. View Roadmap
   └─> http://localhost:8000/roadmap/
       │
       ├─> Click topic to expand
       │   │
       │   └─> API Call: GET /api/roadmap/topic-detail/?topic=Python Basics
       │       │
       │       └─> Backend fetches:
       │           SELECT * FROM TopicResource
       │           WHERE topic = "Python Basics"
       │           ORDER BY order
       │           │
       │           Returns: {
       │             topic_name: "Python Basics",
       │             resources: [
       │               {
       │                 title: "Official Python Tutorial",
       │                 type: "document",
       │                 url: "https://docs.python.org/...",
       │                 description: "..."
       │               },
       │               ...
       │             ]
       │           }
       │
       └─> Display resources:
           📄 Official Python Tutorial
           🎥 Python for Beginners
           📰 Real Python Guide
           [All auto-generated!]
```

---

## 🔄 Detailed LLM Integration Flow

```
┌──────────────────────────────────────────────────────────────┐
│          RESOURCE GENERATION (resource_generator.py)         │
└──────────────────────────────────────────────────────────────┘

Input: topic = "Python Basics", skill_level = "beginner"
│
├─> Check environment variables
│   └─> GEMINI_API_KEY exists?
│       │
│       ├─> YES: Use Gemini API
│       │   │
│       │   ├─> Configure API
│       │   │   import google.generativeai as genai
│       │   │   genai.configure(api_key=GEMINI_API_KEY)
│       │   │   model = genai.GenerativeModel('gemini-pro')
│       │   │
│       │   ├─> Create prompt
│       │   │   """
│       │   │   You are an expert educational resource curator.
│       │   │   Generate curated resources for: "Python Basics"
│       │   │   Skill level: beginner
│       │   │   
│       │   │   Return JSON with: title, type, url, description
│       │   │   Types: document/video/article/link
│       │   │   Generate 5-7 high-quality resources
│       │   │   """
│       │   │
│       │   ├─> Send to Gemini
│       │   │   response = model.generate_content(prompt)
│       │   │   │
│       │   │   Response (2-3 seconds later):
│       │   │   {
│       │   │     "resources": [
│       │   │       {
│       │   │         "title": "Official Python Tutorial",
│       │   │         "type": "document",
│       │   │         "url": "https://docs.python.org/3/tutorial/",
│       │   │         "description": "Comprehensive official tutorial..."
│       │   │       },
│       │   │       {
│       │   │         "title": "Python for Beginners - Full Course",
│       │   │         "type": "video",
│       │   │         "url": "https://www.youtube.com/watch?v=...",
│       │   │         "description": "12-hour complete video course..."
│       │   │       },
│       │   │       ...
│       │   │     ]
│       │   │   }
│       │   │
│       │   ├─> Parse and validate JSON
│       │   │   - Check required fields exist
│       │   │   - Validate resource types
│       │   │   - Ensure URLs are present
│       │   │
│       │   └─> Return valid resources
│       │
│       ├─> NO: Check ANTHROPIC_API_KEY
│       │   │
│       │   ├─> YES: Use Claude API (same flow as above)
│       │   │
│       │   └─> NO: Use fallback generation
│       │       │
│       │       └─> Generate search links
│       │           [
│       │             {
│       │               title: "Official Python Doc",
│       │               type: "document",
│       │               url: "https://google.com/search?q=python+docs",
│       │               description: "Search for Python documentation"
│       │             },
│       │             ...
│       │           ]
│       │
│       └─> Resources generated
           │
           ├─> Save to database
           │   FOR each resource:
           │     TopicResource.objects.create(
           │       topic="Python Basics",
           │       title=resource['title'],
           │       description=resource['description'],
           │       resource_type=resource['type'],
           │       url=resource['url'],
           │       order=index
           │     )
           │
           └─> Return count of resources created
```

---

## 🗄️ Database Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    DATABASE TABLES                          │
└────────────────────────────────────────────────────────────┘

TopicResource Table
┌──────────────┬──────────────┬────────────────────────────┐
│ Column       │ Type         │ Example                    │
├──────────────┼──────────────┼────────────────────────────┤
│ id           │ Integer PK   │ 1                          │
│ topic        │ CharField    │ "Python Basics"            │
│ title        │ CharField    │ "Official Python Tutorial" │
│ description  │ TextField    │ "Comprehensive guide..."   │
│ resource_type│ CharField    │ "document"                 │
│ url          │ URLField     │ "https://docs.python.org/" │
│ order        │ Integer      │ 1                          │
│ created_at   │ DateTime     │ 2024-01-15 10:30:00        │
└──────────────┴──────────────┴────────────────────────────┘

Query Pattern:
━━━━━━━━━━━━━
When user expands topic "Python Basics":

  SELECT * 
  FROM TopicResource 
  WHERE topic = 'Python Basics'
  ORDER BY order ASC

Result:
  → Returns 5-7 resources for that topic
  → All automatically generated by AI
  → Cached for all users (no regeneration needed)
```

---

## 🎯 API Request/Response Flow

```
┌──────────────────────────────────────────────────────────────┐
│              GEMINI API INTERACTION                          │
└──────────────────────────────────────────────────────────────┘

Request:
━━━━━━━━
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent

Headers:
  x-goog-api-key: AIzaSy...
  Content-Type: application/json

Body:
{
  "contents": [{
    "parts": [{
      "text": "You are an expert educational resource curator..."
    }]
  }]
}

Response (2-3 seconds):
━━━━━━━━━━━━━━━━━━━━━━━
{
  "candidates": [{
    "content": {
      "parts": [{
        "text": "{
          \"resources\": [
            {
              \"title\": \"Official Python Tutorial\",
              \"type\": \"document\",
              \"url\": \"https://docs.python.org/3/tutorial/\",
              \"description\": \"Comprehensive official tutorial covering Python fundamentals...\"
            },
            {
              \"title\": \"Python for Beginners - Full Course\",
              \"type\": \"video\",
              \"url\": \"https://www.youtube.com/watch?v=rfscVS0vtbw\",
              \"description\": \"12-hour complete video course covering all Python basics...\"
            },
            {
              \"title\": \"Real Python - Getting Started Guide\",
              \"type\": \"article\",
              \"url\": \"https://realpython.com/start-here/\",
              \"description\": \"Step-by-step beginner guide with code examples...\"
            }
          ]
        }"
      }]
    }
  }]
}

Parse → Validate → Save to DB
```

---

## 📈 Performance Timeline

```
Timeline for Full Roadmap Generation (10 topics):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

0s   │ User clicks "Generate Roadmap"
     │
1s   │ ┌─────────────────────────────────┐
     │ │ Generate Learning Path          │
     │ │ (roadmap_generator.py)          │
2s   │ └─────────────────────────────────┘
     │
     │ ┌─────────────────────────────────┐
     │ │ Start Resource Generation       │
3s   │ │                                 │
     │ │ Topic 1: Python Basics          │
4s   │ │   → Gemini API (2s)            │
5s   │ │   → Save to DB                  │
     │ │                                 │
6s   │ │ Topic 2: Data Structures        │
7s   │ │   → Gemini API (2s)            │
8s   │ │   → Save to DB                  │
     │ │                                 │
9s   │ │ ... (8 more topics)             │
     │ │                                 │
28s  │ │ All resources generated         │
29s  │ └─────────────────────────────────┘
     │
30s  │ Return roadmap to frontend
     │
     │ ✅ Complete!

Total: ~30 seconds for 10 topics
       ~3 seconds per topic
       ~50+ resources generated automatically
```

---

## 🎨 User Interface Flow

```
Roadmap Page View:
━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────┐
│  📚 Your Personalized Learning Roadmap          │
└─────────────────────────────────────────────────┘

Progress Overview:
┌──────────┬──────────┬──────────┬──────────┐
│  📊 45%  │  ✅ 12   │  📝 15   │  ⭐ 850  │
│ Progress │Completed │ Pending  │  Points  │
└──────────┴──────────┴──────────┴──────────┘

Topics:
┌─────────────────────────────────────────────────┐
│ ▼ Week 1: Python Basics          Duration: 3h  │
│                                                  │
│   📖 What You'll Learn:                         │
│   • Variables and data types                    │
│   • Control structures                          │
│   • Functions                                   │
│                                                  │
│   📚 Learning Resources:         [AUTO-GENERATED]│
│   ┌───────────────────────────────────────────┐ │
│   │ 📄 Official Python Tutorial               │ │
│   │    Comprehensive guide to Python basics   │ │
│   │    [View →]                               │ │
│   ├───────────────────────────────────────────┤ │
│   │ 🎥 Python for Beginners - Full Course     │ │
│   │    12-hour complete video course          │ │
│   │    [View →]                               │ │
│   ├───────────────────────────────────────────┤ │
│   │ 📰 Real Python - Getting Started          │ │
│   │    Step-by-step beginner guide            │ │
│   │    [View →]                               │ │
│   └───────────────────────────────────────────┘ │
│                                                  │
│   ✏️ Assignments (2):                           │
│   ┌───────────────────────────────────────────┐ │
│   │ Variables Exercise      [Easy] [100 pts]  │ │
│   │ [Start Assignment]                        │ │
│   └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘

All resources in the gray box are AUTO-GENERATED by AI! 🤖
```

---

## 🔧 Configuration Options

```
Setup Options:
━━━━━━━━━━━━━━

Option 1: Gemini API (Recommended)
──────────────────────────────────
.env file:
  GEMINI_API_KEY=AIzaSy...

Cost: FREE
Speed: Fast (2-3s per topic)
Quality: High
Setup: 2 minutes


Option 2: Claude API (Alternative)
──────────────────────────────────
.env file:
  ANTHROPIC_API_KEY=sk-ant-...

Cost: ~$0.01 per request
Speed: Fast (2-3s per topic)
Quality: Very High
Setup: 5 minutes


Option 3: Fallback Mode (No API)
──────────────────────────────────
.env file:
  (no API keys)

Cost: FREE
Speed: Instant
Quality: Basic (search links)
Setup: 0 minutes (works out of the box)
```

---

This visual guide shows the complete flow from user action to auto-generated resources! 🎨📚🤖
