import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import fg from "fast-glob";
import { ensureDirectories, migratePageFile } from "./lib/migrator.mjs";
import { DIRS } from "./lib/file-mapper.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Main migration function
 */
async function migratePages() {
  console.log("Starting pages migration...");
  console.log(`Source: ${DIRS.JEKYLL_PAGES_DIR}`);
  console.log(`Target: ${DIRS.ASTRO_PAGES_DIR}`);

  // Ensure target directory exists
  ensureDirectories();

  if (!fs.existsSync(DIRS.JEKYLL_PAGES_DIR)) {
    console.error(`ERROR: Jekyll _pages directory not found at ${DIRS.JEKYLL_PAGES_DIR}`);
    process.exit(1);
  }

  const files = await fg(["**/*.md", "**/*.markdown", "**/*.html"], {
    cwd: DIRS.JEKYLL_PAGES_DIR,
    absolute: true,
  });

  console.log(`Found ${files.length} page files to migrate\n`);

  let successCount = 0;
  let errorCount = 0;
  const stylesExtracted = [];

  for (const absPath of files) {
    try {
      const result = await migratePageFile(absPath);
      if (result && result.outputPath) {
        console.log(`✅ ${path.basename(absPath)} → ${path.basename(result.outputPath)}`);
        successCount++;

        // Collect extracted styles
        if (result.extractedStyles) {
          stylesExtracted.push(result.extractedStyles);
          console.log(`   📝 Extracted custom styles from ${result.extractedStyles.page}`);
        }
      }
    } catch (error) {
      console.error(`❌ ${error.message}`);
      errorCount++;
    }
  }

  // Write extracted styles to separate file if any
  if (stylesExtracted.length > 0) {
    const stylesPath = path.join(__dirname, "../src/styles/extracted-page-styles.css");
    const stylesContent = stylesExtracted
      .map(({ page, styles }) => `/* Styles from ${page} */\n${styles}`)
      .join("\n\n");

    // Ensure styles directory exists
    const stylesDir = path.dirname(stylesPath);
    if (!fs.existsSync(stylesDir)) {
      fs.mkdirSync(stylesDir, { recursive: true });
    }

    fs.writeFileSync(stylesPath, stylesContent, "utf8");
    console.log(`\n📦 Extracted styles saved to src/styles/extracted-page-styles.css`);
  }

  console.log(`\n✨ Migration complete!`);
  console.log(`   Success: ${successCount} files`);
  if (errorCount > 0) {
    console.log(`   Errors: ${errorCount} files`);
  }
}

// Run migration
migratePages().catch((error) => {
  console.error("Fatal error during migration:", error);
  process.exit(1);
});
