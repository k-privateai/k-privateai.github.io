import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import yaml from "js-yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const JEKYLL_DATA_DIR = path.join(__dirname, "../../_data");
const ASTRO_DATA_DIR = path.join(__dirname, "../src/data");

// Ensure target directory exists
if (!fs.existsSync(ASTRO_DATA_DIR)) {
  fs.mkdirSync(ASTRO_DATA_DIR, { recursive: true });
}

/**
 * Convert YAML data files to JSON
 */
async function migrateData() {
  console.log("Starting data migration...");
  console.log(`Source: ${JEKYLL_DATA_DIR}`);
  console.log(`Target: ${ASTRO_DATA_DIR}`);

  if (!fs.existsSync(JEKYLL_DATA_DIR)) {
    console.warn(`⚠️  Jekyll _data directory not found at ${JEKYLL_DATA_DIR}`);
    console.log("   Skipping data migration.");
    return;
  }

  const files = fs.readdirSync(JEKYLL_DATA_DIR).filter((f) =>
    /\.(yml|yaml)$/i.test(f)
  );

  if (files.length === 0) {
    console.log("   No YAML files found to migrate.");
    return;
  }

  console.log(`Found ${files.length} data file(s) to migrate\n`);

  let successCount = 0;
  let errorCount = 0;

  for (const filename of files) {
    try {
      const yamlPath = path.join(JEKYLL_DATA_DIR, filename);
      const raw = fs.readFileSync(yamlPath, "utf8");
      const data = yaml.load(raw);

      const jsonFilename = filename.replace(/\.(yml|yaml)$/i, ".json");
      const jsonPath = path.join(ASTRO_DATA_DIR, jsonFilename);

      fs.writeFileSync(jsonPath, JSON.stringify(data, null, 2), "utf8");

      console.log(`✅ ${filename} → ${jsonFilename}`);
      successCount++;
    } catch (error) {
      console.error(`❌ Error migrating ${filename}:`, error.message);
      errorCount++;
    }
  }

  console.log(`\n✨ Data migration complete!`);
  console.log(`   Success: ${successCount} files`);
  if (errorCount > 0) {
    console.log(`   Errors: ${errorCount} files`);
  }
}

// Run migration
migrateData().catch((error) => {
  console.error("Fatal error during migration:", error);
  process.exit(1);
});
