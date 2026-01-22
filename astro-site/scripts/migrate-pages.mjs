import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import fg from "fast-glob";
import matter from "gray-matter";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const JEKYLL_PAGES_DIR = path.join(__dirname, "../../_pages");
const ASTRO_PAGES_DIR = path.join(__dirname, "../src/pages");

// Ensure target directory exists
if (!fs.existsSync(ASTRO_PAGES_DIR)) {
  fs.mkdirSync(ASTRO_PAGES_DIR, { recursive: true });
}

/**
 * Rewrite Liquid syntax to static content or TODO markers
 */
function rewriteLiquid(content) {
  // 1) Remove common site variables
  content = content.replace(/\{\{\s*site\.baseurl\s*\}\}/g, "");
  content = content.replace(/\{\{\s*site\.url\s*\}\}/g, "");

  // 2) Mark includes for manual review
  content = content.replace(
    /\{%\s*include\s+([^%]+)\s*%\}/g,
    "<!-- TODO: JEKYLL_INCLUDE $1 -->"
  );

  // 3) Mark Liquid page variables
  content = content.replace(
    /\{\{\s*page\.[^}]+\}\}/g,
    (m) => `<!-- TODO: LIQUID ${m} -->`
  );

  // 4) Mark Liquid site variables
  content = content.replace(
    /\{\{\s*site\.[^}]+\}\}/g,
    (m) => `<!-- TODO: LIQUID ${m} -->`
  );

  // 5) Mark Liquid loops and conditionals
  content = content.replace(
    /\{%\s*(for|if|unless|elsif|else|endif|endfor|endunless)[^%]*%\}/g,
    (m) => `<!-- TODO: LIQUID ${m} -->`
  );

  // 6) Convert Kramdown notice syntax
  content = content.replace(
    /\n\{:\s*\.notice--(warning|info|primary|success|danger)\s*\}/g,
    '\n<!-- TODO: Convert to Notice component type="$1" -->'
  );

  return content;
}

/**
 * Extract custom CSS from <head> tags
 * Returns: { content, extractedStyles }
 */
function extractCustomStyles(content) {
  const headRegex = /<head>([\s\S]*?)<\/head>/i;
  const match = content.match(headRegex);

  if (!match) {
    return { content, extractedStyles: null };
  }

  const headContent = match[1];
  const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;
  const styles = [];
  let styleMatch;

  while ((styleMatch = styleRegex.exec(headContent)) !== null) {
    styles.push(styleMatch[1].trim());
  }

  if (styles.length === 0) {
    return { content, extractedStyles: null };
  }

  // Remove the entire <head> block from content
  const cleanedContent = content.replace(headRegex, "");

  return {
    content: cleanedContent.trim(),
    extractedStyles: styles.join("\n\n"),
  };
}

/**
 * Determine output filename from permalink or original filename
 */
function getOutputFilename(frontmatter, originalFilename) {
  if (frontmatter.permalink) {
    // Convert permalink to filename
    // /about/ → about.md
    // /activities/ → activities.md
    let filename = frontmatter.permalink.replace(/^\//, "").replace(/\/$/, "");
    if (!filename) filename = originalFilename;

    // Handle nested paths: /foo/bar/ → foo-bar.md
    filename = filename.replace(/\//g, "-");

    return filename.endsWith(".md") ? filename : `${filename}.md`;
  }

  return originalFilename;
}

/**
 * Main migration function
 */
async function migratePages() {
  console.log("Starting pages migration...");
  console.log(`Source: ${JEKYLL_PAGES_DIR}`);
  console.log(`Target: ${ASTRO_PAGES_DIR}`);

  if (!fs.existsSync(JEKYLL_PAGES_DIR)) {
    console.error(`ERROR: Jekyll _pages directory not found at ${JEKYLL_PAGES_DIR}`);
    process.exit(1);
  }

  const files = await fg(["**/*.md", "**/*.markdown", "**/*.html"], {
    cwd: JEKYLL_PAGES_DIR,
    absolute: true,
  });

  console.log(`Found ${files.length} page files to migrate\n`);

  let successCount = 0;
  let errorCount = 0;
  const stylesExtracted = [];

  for (const absPath of files) {
    try {
      const raw = fs.readFileSync(absPath, "utf8");
      const parsed = matter(raw);
      const frontmatter = { ...parsed.data };
      let content = parsed.content;

      // Extract custom styles if present
      const { content: cleanContent, extractedStyles } = extractCustomStyles(content);
      content = cleanContent;

      if (extractedStyles) {
        const basename = path.basename(absPath, path.extname(absPath));
        stylesExtracted.push({
          page: basename,
          styles: extractedStyles,
        });
        console.log(`   📝 Extracted custom styles from ${basename}`);
      }

      // Store original permalink for reference
      if (frontmatter.permalink) {
        frontmatter._originalPermalink = frontmatter.permalink;
      }

      // Remove Jekyll-only keys
      delete frontmatter.layout;
      delete frontmatter.permalink;
      delete frontmatter.published;
      delete frontmatter.author_profile;

      // Rewrite Liquid patterns
      content = rewriteLiquid(content);

      // Determine output filename
      const originalFilename = path.basename(absPath).replace('.markdown', '.md');
      const outputFilename = getOutputFilename(frontmatter, originalFilename);
      const outputPath = path.join(ASTRO_PAGES_DIR, outputFilename);

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

  // Write extracted styles to separate file if any
  if (stylesExtracted.length > 0) {
    const stylesPath = path.join(__dirname, "../src/styles/extracted-page-styles.css");
    const stylesContent = stylesExtracted
      .map(({ page, styles }) => `/* Styles from ${page} */\n${styles}`)
      .join("\n\n");

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
