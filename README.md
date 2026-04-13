# poly-pal

**poly-pal** is a WhatsApp-based language learning chatbot that brings personalized, adaptive language instruction to your phone. It combines the pedagogical framework from **language-learn-mcp** with a modern full-stack application to deliver engaging, CEFR-level-aware lessons directly through WhatsApp.

## Features

### 💬 WhatsApp Integration
Learn languages where you already chat:
- Receive daily language challenges
- Practice vocabulary in natural conversation
- Get instant feedback on your answers
- No app installation needed

### 📊 Personalized Learning Paths
- **CEFR-Level Aware** – Automatically adjusts difficulty and language mixing (A1–C2)
- **Progress Tracking** – Monitors vocabulary mastery and identifies weak areas
- **Adaptive Exercises** – Generates translation, fill-in-the-blank, and multiple-choice questions
- **Word of the Day** – Daily vocabulary reinforcement with contextual usage

### 🎯 Smart Language Balancing
Adjusts the mix of target language vs. English based on proficiency:
- **A1 Learners**: Mostly English with key vocabulary highlighted
- **B1 Learners**: 50/50 mix for conversation building
- **C1 Learners**: Mostly target language with nuanced examples

### 📈 Progress Analytics
- Web dashboard to track vocabulary mastery
- Identify strengths and weaknesses
- Visual progress charts (frontend)
- Personalized learning recommendations

## Architecture

### Backend Stack
- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **AI/LLM**: LangChain + OpenAI / Claude
- **Messaging**: Meta WhatsApp Business API
- **Deployment**: Heroku/Vercel

### Frontend Stack
- **Framework**: Next.js 16+
- **UI**: React 19 + Tailwind CSS
- **Database Client**: Supabase JS SDK
- **Linting**: Biome
- **Deployment**: Vercel

### Project Structure

```
poly-pal/
├── agent/                      # FastAPI backend
│   ├── main.py                 # WhatsApp webhook & endpoints
│   ├── whatsapp.py             # WhatsApp message handling
│   ├── tools.py                # LangChain tools for user interactions
│   ├── word_of_day.py          # Daily challenge scheduler
│   ├── messenger.py            # Message composition utilities
│   ├── db.py                   # Supabase client setup
│   ├── schema.sql              # Database schema
│   ├── requirements.txt        # Python dependencies
│   └── Procfile                # Heroku deployment
│
└── frontend/                   # Next.js web application
    ├── src/
    │   ├── app/                # App routes & pages
    │   ├── components/         # React components
    │   └── lib/                # Utilities & helpers
    ├── public/                 # Static assets
    ├── package.json            # Node dependencies
    ├── tsconfig.json           # TypeScript config
    ├── biome.json              # Linting config
    └── next.config.ts          # Next.js config
```

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account
- Meta WhatsApp Business API credentials
- Claude / OpenAI API key

### Backend Setup

```bash
cd agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase, Meta, OpenAI/Claude keys, etc.

# Initialize database
psql -h localhost -U your_supabase_user -d your_database < schema.sql

# Run the server
python main.py
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Add your Supabase URL and API key

# Run development server
npm run dev
```

Visit `http://localhost:3000` to see the dashboard.

## Usage

### For Users

1. **Save poly-pal's WhatsApp number** (from your admin dashboard)
2. **Send "Hi"** to start the onboarding process
3. **Select your target language** and proficiency level (A1–C2)
4. **Receive daily challenges** and practice vocabulary
5. **Check your progress** on the web dashboard

### For Developers

#### Running Both Services

```bash
# Terminal 1: Backend
cd agent && python main.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

#### Key Endpoints

- `POST /webhook` – WhatsApp message webhook
- `GET /webhook` – WhatsApp verification
- `POST /cron/word-of-day` – Scheduled daily challenge

#### Available Tools (from `agent/tools.py`)

```python
# Save learner progress
save_progress(word: str, correct: bool) -> str

# Get weak vocabulary
get_weak_words(limit: int = 5) -> str

# Generate an exercise
generate_exercise(type: str, topic: str = "") -> str
# type: "translation", "fill_in", or "multiple_choice"

# Get language mixing recommendation
get_language_balance() -> str
```

## Connection to language-learn-mcp

**poly-pal** is built on top of **language-learn-mcp**, the pedagogical framework for language learning. Here's how they work together:

### language-learn-mcp Provides:
- 🎯 CEFR-level definitions and vocabulary lists
- 🛠️ Exercise generation algorithms
- 📊 Response scoring mechanisms
- 🔄 Learner progress analysis tools
- 🌍 Language-specific pedagogy

### poly-pal Provides:
- 💬 WhatsApp integration layer
- 📦 Production database (Supabase) for user data
- 🖥️ Web dashboard for progress tracking
- ⏰ Scheduling & cron jobs
- 🎨 Full-stack user experience

**In essence**: language-learn-mcp is the *engine*, poly-pal is the *vehicle*. Together they deliver a complete, modern language learning experience.

## Environment Variables

### Backend (`.env`)
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# OpenAI / Claude
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Meta WhatsApp
META_VERIFY_TOKEN=your-verify-token
META_ACCESS_TOKEN=your-access-token
WHATSAPP_BUSINESS_ACCOUNT_ID=your-account-id

# Cron jobs
CRON_SECRET=your-secret-token
```

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Deployment

### Backend (Heroku)

```bash
# Create Heroku app
heroku create poly-pal-api

# Set environment variables
heroku config:set SUPABASE_URL=... OPENAI_API_KEY=... etc.

# Deploy
git push heroku main
```

### Frontend (Vercel)

```bash
# Vercel CLI
vercel deploy
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Testing

### Backend
```bash
cd agent
pytest tests/
```

### Frontend
```bash
cd frontend
npm run test
npm run lint
npm run format
```

## Contributing

We welcome contributions! Areas of focus:
- Additional exercise types
- Language packs (new languages)
- Mobile app (React Native)
- Gamification features
- AI tutor improvements

## License

MIT License

## Author

Abdullah Hasan

## Related Projects

- **[language-learn-mcp](https://github.com/abdullah1186/language-learn-mcp)** – Pedagogical framework powering poly-pal

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Contact the author directly

---

**Start learning languages today, one WhatsApp message at a time! 🌍📱**