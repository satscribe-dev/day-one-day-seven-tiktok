// Day one, day seven — entry program (Node 22, standard library only).
// The entry is the video itself: this program only copies VIDEO.json
// from the repository root to /output, where the gate reads it.
// It validates that VIDEO.json parses and names a url first, so a
// broken file fails loudly instead of shipping a bad copy.
// Run locally as: mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const videoPath = join(botDir, "VIDEO.json");
const video = JSON.parse(readFileSync(videoPath, "utf8"));
if (typeof video !== "object" || video === null || typeof video.url !== "string") {
  console.error("VIDEO.json must be an object with a string url");
  process.exit(1);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(videoPath, join(outDir, "VIDEO.json"));
