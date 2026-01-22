import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import fg from "fast-glob";
import matter from "gray-matter";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const JEKYLL_POSTS_DIR = path.join(__dirname, "../../_posts");
const ASTRO_POSTS_DIR = path.join(__dirname, "../src/content/posts");

// Ensure target directory exists
if (!fs.existsSync(ASTRO_POSTS_DIR)) {
  fs.mkdirSync(ASTRO_POSTS_DIR, { recursive: true });
}

/**
 * Extract date from Jekyll post filename
 * Pattern: YYYY-MM-DD-{TZ} - {Title}.markdown
 * Example: 2024-10-07-PDT - K-PAI seminar series invitation.markdown
 */
function inferDateFromFilename(file) {
  const base = path.basename(file);
  const match = base.match(/^(\d{4})-(\d{2})-(\d{2})-[A-Z]+ - /);
  if (!match) return null;
  const [, year, month, day] = match;
  return `${year}-${month}-${day}`;
}

/**
 * Generate a clean slug from filename
 * Removes date and timezone prefix, converts to lowercase kebab-case
 */
function generateSlug(filename) {
  const base = path.basename(filename, path.extname(filename));
  // Remove date and timezone prefix: "YYYY-MM-DD-TZ - "
  const withoutDate = base.replace(/^\d{4}-\d{2}-\d{2}-[A-Z]+ - /, "");
  // Convert to lowercase and replace spaces with hyphens
  return withoutDate
    .toLowerCase()
    .replace(/[^\w\s-]/g, "") // Remove special chars
    .replace(/\s+/g, "-") // Replace spaces with hyphens
    .replace(/-+/g, "-") // Collapse multiple hyphens
    .trim();
}

/**
 * Rewrite Liquid syntax to static content or TODO markers
 */
function rewriteLiquid(content) {
  // 1) Remove common site variables (empty in GitHub Pages)
  content = content.replace(/\{\{\s*site\.baseurl\s*\}\}/g, "");
  content = content.replace(/\{\{\s*site\.url\s*\}\}/g, "");

  // 2) Mark includes for manual review
  content = content.replace(
    /\{%\s*include\s+([^%]+)\s*%\}/g,
    "<!-- TODO: JEKYLL_INCLUDE $1 -->"
  );

  // 3) Mark Liquid date filters and other page variables
  content = content.replace(
    /\{\{\s*page\.[^}]+\}\}/g,
    (m) => `<!-- TODO: LIQUID ${m} -->`
  );

  // 4) Convert Kramdown notice syntax to TODO markers
  // Pattern: {: .notice--warning}
  content = content.replace(
    /\n\{:\s*\.notice--(warning|info|primary|success|danger)\s*\}/g,
    '\n<!-- TODO: Convert to Notice component type="$1" -->'
  );

  return content;
}

/**
 * Main migration function
 */
async function migratePosts() {
  console.log("Starting posts migration...");
  console.log(`Source: ${JEKYLL_POSTS_DIR}`);
  console.log(`Target: ${ASTRO_POSTS_DIR}`);

  if (!fs.existsSync(JEKYLL_POSTS_DIR)) {
    console.error(`ERROR: Jekyll _posts directory not found at ${JEKYLL_POSTS_DIR}`);
    process.exit(1);
  }

  const files = await fg(["**/*.md", "**/*.markdown"], {
    cwd: JEKYLL_POSTS_DIR,
    absolute: true,
  });

  console.log(`Found ${files.length} post files to migrate\n`);

  let successCount = 0;
  let errorCount = 0;

  for (const absPath of files) {
    try {
      const raw = fs.readFileSync(absPath, "utf8");
      const parsed = matter(raw);
      const frontmatter = { ...parsed.data };
      let content = parsed.content;

      // Inject date from filename if missing
      if (!frontmatter.date) {
        const inferredDate = inferDateFromFilename(absPath);
        if (inferredDate) {
          frontmatter.date = inferredDate;
        } else {
          console.warn(`⚠️  Could not infer date from filename: ${path.basename(absPath)}`);
        }
      }

      // Preserve custom permalink if exists
      if (frontmatter.permalink) {
        frontmatter._legacyPermalink = frontmatter.permalink;
      }

      // Generate slug for Content Collections
      const slug = generateSlug(path.basename(absPath));
      if (slug) {
        frontmatter.slug = slug;
      }

      // Remove Jekyll-only keys
      delete frontmatter.layout;
      delete frontmatter.permalink;
      delete frontmatter.published;

      // Rewrite Liquid patterns in content
      content = rewriteLiquid(content);

      // Generate output filename (use slug or original filename)
      const outputFilename = slug ? `${slug}.md` : path.basename(absPath).replace('.markdown', '.md');
      const outputPath = path.join(ASTRO_POSTS_DIR, outputFilename);

      // Write migrated file
      const output = matter.stringify(content, frontmatter);
      fs.writeFileSync(outputPath, output, "utf8");

      console.log(`✅ ${path.basename(absPath)} → ${outputFilename}`);
      successCount++;
    } catch (error) {
      console.error(`❌ Error migrating ${path.basename(absPath)}:`, error.message);
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
