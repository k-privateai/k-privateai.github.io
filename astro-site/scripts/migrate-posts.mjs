import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import fg from "fast-glob";
import { ensureDirectories, migratePostFile } from "./lib/migrator.mjs";
import { DIRS } from "./lib/file-mapper.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Main migration function
 */
async function migratePosts() {
  console.log("Starting posts migration...");
  console.log(`Source: ${DIRS.JEKYLL_POSTS_DIR}`);
  console.log(`Target: ${DIRS.ASTRO_POSTS_DIR}`);

  // Ensure target directory exists
  ensureDirectories();

  if (!fs.existsSync(DIRS.JEKYLL_POSTS_DIR)) {
    console.error(`ERROR: Jekyll _posts directory not found at ${DIRS.JEKYLL_POSTS_DIR}`);
    process.exit(1);
  }

  const files = await fg(["**/*.md", "**/*.markdown"], {
    cwd: DIRS.JEKYLL_POSTS_DIR,
    absolute: true,
  });

  console.log(`Found ${files.length} post files to migrate\n`);

  let successCount = 0;
  let errorCount = 0;

  for (const absPath of files) {
    try {
      const outputPath = await migratePostFile(absPath);
      if (outputPath) {
        console.log(`✅ ${path.basename(absPath)} → ${path.basename(outputPath)}`);
        successCount++;
      }
    } catch (error) {
      console.error(`❌ ${error.message}`);
      errorCount++;
    }
  }

  console.log(`\n✨ Migration complete!`);
  console.log(`   Success: ${successCount} files`);
  if (errorCount > 0) {
    console.log(`   Errors: ${errorCount} files`);
  }
}

// Run migration
migratePosts().catch((error) => {
  console.error("Fatal error during migration:", error);
  process.exit(1);
});
