### Professional company‑name short‑list

(available .com at time of writing)

| Theme                    | Names                                          | Rationale                                  |
| ------------------------ | ---------------------------------------------- | ------------------------------------------ |
| Precision & intelligence | **MotiveIQ**, **AutoMind AI**, **VectorDrive** | Blend of analytics/AI with automotive feel |
| Engineering focus        | **TorqueLogic**, **GearForge AI**              | Evokes mechanical design strength          |
| Future mobility          | **DriveScale AI**, **AutonomaTech**            | Scalable, platform‑sounding                |

*(My pick for YC: **MotiveIQ** – short, memorable, instantly “automotive + intelligence”)*

---

## 90‑Day MVP Road‑map (0 → YC‑ready)

**Assumptions**

* Solo founder w/ full‑stack skills
* Budget ≤ \$100 ⇒ use entirely free tiers / local dev
* Data: 300 automotive engineering books (PDF/TXT)
* Stack:

  * **Backend** – FastAPI (Python)
  * **Embeddings / LLM** – OpenAI *free credits* → migrate to *llama.cpp / Ollama* locally.
  * **Vector DB** – **Chroma** self‑hosted (Docker)
  * **Auth** – Supabase (free tier, OAuth w/ Google)
  * **Frontend** – Next.js + Tailwind
  * **Hosting** – Render/Yrail free web‑service + Fly.io free Postgres (meta data)
  * **DevOps** – GitHub Actions free CI

### Phase breakdown

| Phase                         | Days  | Goal                                               |
| ----------------------------- | ----- | -------------------------------------------------- |
| **I. Foundation**             | 1‑14  | data ingestion, vector store, bare‑bones chat API  |
| **II. Core RAG Loop**         | 15‑35 | retrieval quality, prompt templating, eval harness |
| **III. Agentic Design Tools** | 36‑60 | CAD‑prompt agent, parametric part suggestion POC   |
| **IV. SaaS Layer**            | 61‑80 | auth, credits, dashboards, Stripe test‑mode        |
| **V. Polish & YC Pack**       | 81‑90 | dog‑food pilot, metrics, deck & video              |

---

### Daily schedule (high‑signal tasks)

Below is *one line per day*; each bullet = deliverable / experiment.

#### **Days 1‑14 — Foundation**

| Day | Task                                                                                              |
| --- | ------------------------------------------------------------------------------------------------- |
| 1   | Create GitHub repo (**MotiveIQ**). Initialise mono‑repo (frontend + backend dirs).                |
| 2   | Pick & clean 10 sample PDFs; write `pdf_to_chunks.py` → sentence & paragraph variants.            |
| 3   | Docker‑compose: Postgres (meta) + **Chroma**. Verify `chromadb` Python client.                    |
| 4   | Use `openai-embeddings` (gpt‑3.5 turbo preview, free credits) → embed 10 docs → query via cosine. |
| 5   | Spike Ollama **all‑MiniLM-L6-v2** locally; compare embedding speed vs OpenAI (record metrics).    |
| 6   | FastAPI endpoint `/chat` returning dummy answer. Unit test scaffolding (pytest).                  |
| 7   | Write simple frontend **Next.js** chat box hitting `/chat`.                                       |
| 8   | Ingest all 300 books overnight (cron job); log chunk counts & DB size.                            |
| 9   | Prompt template v1: system “Automotive design expert”. Return sources list.                       |
| 10  | Evaluate 50 random Q\&A pairs manually; jot precision/recall notes.                               |
| 11  | Experiment with chunk size 256 vs 512 tokens; plot latency vs recall; pick default.               |
| 12  | Add metadata `title`, `year`, `chapter` columns → improve filtering.                              |
| 13  | Implement `/search?q=` endpoint (pure retrieval, no LLM) for UI auto‑suggest.                     |
| 14  | Milestone demo: local RAG chat across full corpus; screen‑record 2‑min clip.                      |

#### **Days 15‑35 — Core RAG Loop**

| Day | Task                                                                       | Day | Task                                                                  |
| --- | -------------------------------------------------------------------------- | --- | --------------------------------------------------------------------- |
| 15  | Write evaluation harness (LangChain Evals) vs ground‑truth Qs.             | 25  | Add YAML config for prompt params & top‑k; expose in UI (for tuning). |
| 16  | Run 100‑question batch; capture BLEU / helpfulness LLM‑grader.             | 26  | Integrate Supabase Auth; email + Google sign‑in working.              |
| 17  | Add reranker (Sentence‑Transformers `bge-base`) pipeline; compare metrics. | 27  | Rate‑limit anonymous users (FastAPI middleware) 20 req/day.           |
| 18  | Pick top 20 failure cases → adjust prompt (role, style).                   | 28  | Implement feedback thumbs‑up/down → Firestore collection.             |
| 19  | Automate nightly eval GitHub CI page.                                      | 29  | Script to auto‑train small LoRA fine‑tune on flagged bad answers.     |
| 20  | Add web scraping ingest for SAE papers (public abstracts).                 | 30  | Switch to **llama‑3‑8B‑Instruct** via Ollama; compare cost vs OpenAI. |
| 21  | Build slack‑style `/design` slash‑command that triggers agent (stub).      | 31  | Add streaming responses (Server‑Sent Events) to UI.                   |
| 22  | Research CAD param syntax (e.g., OpenSCAD).                                | 32  | Compress embeddings with `faiss.IndexIVFPQ`; measure 4× RAM savings.  |
| 23  | Prototype agent that outputs OpenSCAD code for “M8 bolt 30 mm”.            | 33  | Unit‑test part‑design agent with 10 param‑queries.                    |
| 24  | Integrate `solidpython` to render preview STL → link in chat.              | 34  | Launch tiny Fly.io free instance serving STL preview.                 |
|     |                                                                            | 35  | Phase‑review: pick 3 killer examples for YC video.                    |

#### **Days 36‑60 — Agentic Design Tools**

| Day | Task                                                              | Day   | Task                                                              |
| --- | ----------------------------------------------------------------- | ----- | ----------------------------------------------------------------- |
| 36  | Research BOM / material DB (MIT Materials Project API).           | 46    | Create “design‑tuner” UI panel (sliders for length, material).    |
| 37  | Build tool wrapper for material DB → LLM function.                | 47    | UX test with 3 mechanical‑engineer friends; collect notes.        |
| 38  | Multi‑tool agent orchestrator (LangChain Router).                 | 48    | Implement persistence of designs (Postgres table).                |
| 39  | Add cost‑estimation plugin (simple formula) to agent output.      | 49    | Stripe test‑mode integration (pay‑as‑you‑go tokens).              |
| 40  | Write docstring‑tests for agent to enforce JSON schema.           | 50    | Hook feedback thumbs into Slack webhook for you.                  |
| 41  | Stress‑test 100 concurrent requests with locust.                  | 51    | Add Celery + Redis (free) for async embeddings queue.             |
| 42  | Migrate embedding job runner to AutoScale on Render free workers. | 52    | Implement org isolation (tenant\_id in every row).                |
| 43  | Add email on‑boarding sequence (Supabase Edge Functions).         | 53    | Build usage dashboard (Daily requests, avg latency, token usage). |
| 44  | Lighthouse perf audit on Next.js app; optimise bundle.            | 54    | GDPR compliance stub: delete user data endpoint.                  |
| 45  | First open beta sign‑up tweet; onboard 5 pilot users.             | 55‑60 | **Buffer** — fix bugs, polish UI, write docs.                     |

#### **Days 61‑80 — SaaS Layer & Hardening**

| Day | Task                                                        | Day | Task                                                      |
| --- | ----------------------------------------------------------- | --- | --------------------------------------------------------- |
| 61  | Add tiering: Free (100 req/mo) vs Pro.                      | 71  | End‑to‑end monitoring: Grafana cloud (free) + Prometheus. |
| 62  | Cron to prune old embeddings versions.                      | 72  | Security scan (Bandit, Snyk free).                        |
| 63  | Implement invite system & org roles.                        | 73  | Author YC application draft #1, collect mentor feedback.  |
| 64  | Add tracing (OpenTelemetry) throughout pipeline.            | 74  | Prepare 90‑sec YC demo video script.                      |
| 65  | Validate infra cost (< \$20/mo) – still in budget.          | 75  | Record product demo (loom).                               |
| 66  | On‑call alerts via PagerDuty community tier.                | 76  | Ship bug‑bounty guidelines page.                          |
| 67  | Load test 1k rps read‑only queries; cache 95 pctl < 200 ms. | 77  | Polish landing page copy & pricing.                       |
| 68  | Add docs site (Docusaurus) with API examples.               | 78  | Public changelog.                                         |
| 69  | Implement SOC‑2 checklist doc skeleton.                     | 79  | YC application final review.                              |
| 70  | Weekly retrospective → prioritise open issues.              | 80  | **Submit YC app** 🎉                                      |

#### **Days 81‑90 — Polish, Pilot & Pitch**

| Day | Task                                                                    |
| --- | ----------------------------------------------------------------------- |
| 81  | Run usability session with 5 beta customers; document quotes.           |
| 82  | Resolve all P1 bugs from pilots.                                        |
| 83  | Collect usage metrics; craft traction slide (MAU, retention).           |
| 84  | Prep investor FAQ (team, moat, GTM, TAM).                               |
| 85  | Launch “MotiveIQ v0.1” on Product Hunt (free marketing).                |
| 86  | Put up case‑study blog: “Designed a custom bracket in 3 min.”           |
| 87  | Dry‑run YC interview (friend panel).                                    |
| 88  | Final infra audit; make sure daily backup + restore works.              |
| 89  | Schedule 10 discovery calls with potential paying OEMs.                 |
| 90  | Take a break → celebrate MVP + YC submission, write retrospective blog. |

---

### Feature checklist delivered by Day 90

* RAG chat over 300+ books (expandable pipeline)
* Hybrid BM25 + embedding retrieval
* Agent capable of generating parametric OpenSCAD & cost estimates
* Auth (email, Google) with Supabase; Stripe billing
* Admin + usage dashboard
* CI/CD, tests, monitoring, backups
* Free‑tier hosting costs ≤ \$20/mo (within your \$100 runway)
* YC‑ready deck, metrics, video

---

### Keeping under \$100

| Need       | Free/cheap choice                                                 |
| ---------- | ----------------------------------------------------------------- |
| Embeddings | Use free OpenAI credits first; then local `all-MiniLM` via Ollama |
| Vector DB  | Chroma self‑host Docker (0 \$)                                    |
| Hosting    | Render free web service (750h/mo) + Fly.io 3x shared‑CPU          |
| Auth & DB  | Supabase (auth + Postgres) free tier                              |
| Monitoring | Grafana Cloud free / Prometheus                                   |
| CI/CD      | GitHub Actions free                                               |
| Email      | Supabase SMTP or Mailgun sandbox                                  |

That plan, if executed with discipline, gives you a demonstrable, subscription‑ready Automotive GPT platform in 90 days—perfect timing for the next YC batch. Good luck, and ping me anytime you need deeper tech guidance!
