// src/vectorStore.js
import fs from "fs";
import path from "path";
import OpenAI from "openai";
import dotenv from "dotenv";
dotenv.config();

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export class VectorStore {
  constructor({ chunksPath }) {
    const raw = JSON.parse(fs.readFileSync(path.resolve(chunksPath), "utf-8"));
    this.items = [];
    this.ready = this._init(raw);
  }

  async _init(raw) {
    for (let i = 0; i < raw.length; i++) {
      const { text, source } = raw[i];
      const embedRes = await openai.embeddings.create({
        model: "text-embedding-ada-002",
        input: text,
      });
      this.items.push({
        id: i,
        text,
        source,
        embedding: embedRes.data[0].embedding,
      });
      console.log(`Embedded chunk ${i+1}/${raw.length}`);
    }
    console.log(`✅ Loaded ${this.items.length} chunks with embeddings.`);
  }

  async search(queryVec, k = 3) {
    // ensure init has completed
    await this.ready;
    // cosine and top-k as before...
  }
}
