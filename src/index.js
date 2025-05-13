// src/index.js
import express from "express";
import bodyParser from "body-parser";
import OpenAI from "openai";
import { VectorStore } from "./vectorStore.js";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(bodyParser.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Your vector store initialization stays the same:
const vs = new VectorStore({ chunksPath: "./embeddings/chunks.json" });
// and before handling a chat request, await vs.ready

function buildPrompt(userQuestion, passages) {
  const summary = `You are an expert engine-design mentor. Answer clearly:`;
  const retrieved = passages
    .map((p, i) => `Source ${i + 1}: ${p.text.slice(0, 200)}...`)
    .join("\n\n");

  return `
${summary}

User: "${userQuestion}"

Reference material:
${retrieved}

Instructions:
1. Give a 1-sentence summary.
2. List 3–5 bullet points.
3. Ask a clarifying question at end.
`;
}

// src/index.js — replace your existing /chat block with this:
app.post("/chat", async (req, res) => {
  try {
    const { question } = req.body;
    console.log("🟢 Received question:", question);

    // 1) Embed
    console.log("–> embedding…");
    const embedRes = await openai.embeddings.create({
      model: "text-embedding-ada-002",
      input: question,
    });
    console.log("–> embedRes.data:", embedRes.data);

    const qVec = embedRes.data?.[0]?.embedding;
    if (!qVec) throw new Error("No embedding returned");

    // 2) Retrieve
    console.log("–> retrieving top chunks…");
    const topK = vs.search(qVec, 3);
    console.log("–> topK:", topK);

    // 3) Build prompt
    const prompt = buildPrompt(question, topK);
    console.log("–> prompt snippet:", prompt.slice(0, 200), "...");

    // 4) LLM call
    console.log("–> calling chat completion…");
    const chatRes = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2,
    });
    console.log("–> chatRes.choices[0]:", chatRes.choices[0]);

    const answer = chatRes.choices[0].message.content.trim();
    return res.json({ answer, sources: topK.map((p) => p.id) });
  } catch (err) {
    console.error("❌ Chat handler error:", err);
    return res.status(500).json({
      error: err.message,
      stack: err.stack?.split("\n").slice(0, 5),
    });
  }
});

app.post("/feedback", (req, res) => {
  const { question, intentId, rating, correction } = req.body;
  console.log({ question, intentId, rating, correction });
  res.json({ status: "ok" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Listening on ${PORT}`));
