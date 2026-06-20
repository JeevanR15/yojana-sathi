<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00C896,100:FF9933&height=220&section=header&text=Yojana%20Sathi&fontSize=68&fontColor=ffffff&fontAlignY=36&desc=Voice-Powered%20Welfare%20Scheme%20Finder%20for%20Rural%20India&descAlignY=58&descAlign=50&animation=fadeIn" width="100%"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&size=18&pause=1000&color=00C896&center=true&vCenter=true&width=620&lines=Speak+your+situation+in+any+Indian+language;AI+understands+your+life%2C+not+just+keywords;MongoDB+Atlas+%24vectorSearch+semantic+RAG;Schemes+explained+back+in+simple+spoken+Hindi;No+reading.+No+typing.+No+barrier." alt="Typing SVG"/>

<br/><br/>

<a href="https://s3.hackprix.tech/"><img src="https://img.shields.io/badge/HackPrix-S3-00C896?style=for-the-badge&labelColor=0D1117&logo=devpost&logoColor=00C896"/></a>
<img src="https://img.shields.io/badge/Hero-MongoDB%20%24vectorSearch-13AA52?style=for-the-badge&labelColor=0D1117&logo=mongodb&logoColor=white"/>
<img src="https://img.shields.io/badge/Voice-Sarvam%20AI-C77D3A?style=for-the-badge&labelColor=0D1117&logo=audacity&logoColor=white"/>
<img src="https://img.shields.io/badge/LLM-Gemini%202.0%20Flash-3B6FB0?style=for-the-badge&labelColor=0D1117&logo=googlegemini&logoColor=white"/>

<br/>

<img src="https://img.shields.io/badge/Frontend-Next.js%2014-0D1117?style=flat-square&logo=nextdotjs&logoColor=white"/>
<img src="https://img.shields.io/badge/Backend-FastAPI-0D1117?style=flat-square&logo=fastapi&logoColor=009688"/>
<img src="https://img.shields.io/badge/Styling-Tailwind-0D1117?style=flat-square&logo=tailwindcss&logoColor=06B6D4"/>
<img src="https://img.shields.io/badge/Made%20for-Rural%20Bharat-0D1117?style=flat-square&logo=india&logoColor=FF9933"/>

</div>

<br/>

A voice-first AI agent that helps non-literate rural Indians discover and apply for
government welfare schemes. The user **speaks her situation in her own language**, and
the system finds the welfare schemes she qualifies for and **explains them back in
simple spoken Hindi** — no reading or typing required.

> _"Main 60 saal ki vidhwa hoon, Bihar mein rehti hoon, BPL card hai, zameen hai"_
> → PM Kisan, Widow Pension, Ayushman Bharat, and more.

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=rect&color=0:00C896,100:FF9933&height=3&width=100%25&section=header" width="100%"/>

</div>

## 🧠 How it works (the architecture, for judges)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 🎙  VOICE  —  spoken aloud in any Indian language                    │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [1]  SARVAM AI · speech-to-text (saarika:v2)   ──►  transcript       │
│      built for Indian languages / code-mixing / dialects             │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [2]  GEMINI 2.0 FLASH · profile extraction   ──►  structured JSON    │
│      {age, gender, state, occupation, bpl_card, land, widow, ...}    │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [3]  GEMINI text-embedding-004   ──►  768-dim vector                 │
│      semantic meaning of her whole situation                         │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [4]  MONGODB ATLAS · $vectorSearch (RAG)   ──►  top 3 schemes        │
│      "poor widow farmer"  ≈  "BPL female cultivator with             │
│      spousal bereavement"  —  no keyword overlap needed              │
│                                                                      │
│      ★  THE TECHNICAL HERO — true semantic retrieval, not keywords   │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [5]  GEMINI 2.0 FLASH · simple-Hindi explanation per scheme          │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ [6]  SARVAM AI · text-to-speech (bulbul:v1)   ──►  spoken Hindi audio│
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 🔊  She HEARS which schemes she qualifies for and what to do         │
└──────────────────────────────────────────────────────────────────────┘
```

The **technical hero** is step 4: MongoDB Atlas Vector Search (`$vectorSearch`) doing
true semantic retrieval (RAG), not keyword lookup.

## 🛠️ Tech stack

| Layer       | Tech                                                                 |
|-------------|----------------------------------------------------------------------|
| Frontend    | Next.js 14 (App Router), Tailwind CSS, Spline 3D orb, MediaRecorder   |
| Backend     | Python FastAPI                                                       |
| Voice       | Sarvam AI — STT `saarika:v2`, TTS `bulbul:v1`                         |
| LLM         | Google Gemini 2.0 Flash + `text-embedding-004`                       |
| Database    | MongoDB Atlas (M0) with Atlas Vector Search                          |

## 🚀 How to run

### 1. Backend

```bash
cd backend
python -m venv venv               # optional but recommended
venv\Scripts\activate             # Windows (use: source venv/bin/activate on mac/linux)
pip install -r requirements.txt

# Fill in backend/.env with your three API keys, then:
python seed_schemes.py            # run ONCE — embeds + inserts the 15 schemes
# ...then create the Vector Search index in Atlas (the script prints how) ...
uvicorn main:app --reload --port 8000
```

Verify it's alive: open <http://localhost:8000/health> → `{"status":"ok", ...}`

### 2. Frontend

```bash
cd frontend
npm install
# Fill in frontend/.env.local with NEXT_PUBLIC_BACKEND_URL + SARVAM_API_KEY
npm run dev
```

Open <http://localhost:3000>

## 🔑 Environment variables

**backend/.env**
```
SARVAM_API_KEY=...
GEMINI_API_KEY=...
MONGODB_URI=mongodb+srv://...
```

**frontend/.env.local**
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
SARVAM_API_KEY=...
```

> ⚠️ Both `.env` files are gitignored. Never commit your keys.

## 🗄️ MongoDB Vector Search index

After `python seed_schemes.py`, the script prints the exact steps. In short: Atlas UI →
your cluster → **Search → Create Search Index → Atlas Vector Search**, database
`yojana_sathi`, collection `schemes`, index name **`vector_index`**:

```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 768, "similarity": "cosine" }
  ]
}
```

Wait ~2-3 min until the index status is **ACTIVE** before querying.

## 🧯 Troubleshooting

| Problem | Fix |
|---|---|
| `/match` returns "Could not search schemes" | The Vector Search index isn't ACTIVE yet, or its name isn't `vector_index`. |
| Sarvam STT returns empty / 400 | Audio format issue — see note below. Try speaking longer (2-5s). |
| `pymongo` can't resolve `mongodb+srv` | `pip install "pymongo[srv]"` (pulls dnspython). |
| Spline orb doesn't appear | Expected on slow wifi — a pure-CSS glowing orb fallback renders automatically. |
| Mic permission denied | A text-input fallback appears so you can type the situation instead. |

**Audio format note:** the browser records `audio/webm`. Sarvam's STT generally accepts
this. If your demo machine's browser produces an unsupported format, the backend logs
the exact Sarvam error to the console so you can diagnose quickly.

## 💸 API-cost discipline (built in)

- Gemini embeddings are called **only** during seeding and on a real user query.
- Sarvam TTS is called **only** for the final spoken explanation of a real result.
- Every external API call prints a `console.log` / `print` line first, so you can see
  exactly when credits are being spent.

<div align="center">

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:FF9933,100:00C896&height=120&section=footer&animation=fadeIn" width="100%"/>

**Built for Bharat — HackPrix S3**

</div>
