// scripts/buildMeta.js
import fs from "fs";
import OpenAI from "openai";
import dotenv from "dotenv";
dotenv.config();

async function main() {
  const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
  const chunks = JSON.parse(fs.readFileSync("embeddings/chunks.json", "utf-8"));

  const meta = [];
  for (let i = 0; i < chunks.length; i++) {
    const text = chunks[i].text;
    const res = await openai.embeddings.create({
      model: "text-embedding-ada-002",
      input: text,
    });
    meta.push({
      id: i,
      text,
      embedding: res.data[0].embedding,
      source: chunks[i].source
    });
    console.log(`Embedded chunk ${i+1}/${chunks.length}`);
  }

  fs.writeFileSync(
    "data/engine_design/meta.json",
    JSON.stringify(meta, null, 2)
  );
  console.log("✅ meta.json written");
}

main().catch(console.error);
