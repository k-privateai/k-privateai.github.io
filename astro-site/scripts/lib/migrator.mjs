import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { jekyllToAstroPath, generateSlug, DIRS } from "./file-mapper.mjs";
import { logger } from "./logger.mjs";

/**
 * Ensure target directories exist
 */
export function ensureDirectories() {
  const dirs = [DIRS.ASTRO_POSTS_DIR, DIRS.ASTRO_PAGES_DIR, DIRS.ASTRO_DATA_DIR];
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }
}

/**
 * Extract date from Jekyll post filename
 * Pattern: YYYY-MM-DD-{TZ} - {Title}.markdown
 * Example: 2024-10-07-PDT - K-PAI seminar series invitation.markdown
 */
export function inferDateFromFilename(file) {
  const base = path.basename(file);
  const match = base.match(/^(\d{4})-(\d{2})-(\d{2})-[A-Z]+ - /);
  if (!match) return null;
  const [, year, month, day] = match;
  return `${year}-${month}-${day}`;
}

/**
 * Rewrite Liquid syntax to static content or TODO markers
 */
export function rewriteLiquid(content) {
  // 1) Remove common site variables (empty in GitHub Pages)
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

  // 6) Convert Kramdown notice syntax to TODO markers
  // Pattern: {: .notice--warning}
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
export function extractCustomStyles(content) {
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
 * Check for file collision and return whether to skip
 */
export function checkCollision(targetPath, sourcePath) {
  if (!fs.existsSync(targetPath)) {
    return false; // No collision, proceed
  }

  const targetMtime = fs.statSync(targetPath).mtime;
  const sourceMtime = fs.statSync(sourcePath).mtime;

  if (sourceMtime < targetMtime) {
    logger.warn(`${path.basename(targetPath)} is newer, skipping older source`);
    return true; // Skip
  }

  logger.warn(`Overwriting ${path.basename(targetPath)} with newer source`);
  return false; // Proceed with overwrite
}

/**
 * Migrate a single Jekyll post file to Astro
 */
export async function migratePostFile(sourcePath) {
  try {
    const raw = fs.readFileSync(sourcePath, "utf8");
    const parsed = matter(raw);
    const frontmatter = { ...parsed.data };
    let content = parsed.content;

    // Inject date from filename if missing
    if (!frontmatter.date) {
      const inferredDate = inferDateFromFilename(sourcePath);
      if (inferredDate) {
        frontmatter.date = inferredDate;
      } else {
        logger.warn(`Could not infer date from filename: ${path.basename(sourcePath)}`);
      }
    }

    // Preserve custom permalink if exists
    if (frontmatter.permalink) {
      frontmatter._legacyPermalink = frontmatter.permalink;
    }

    // Generate slug for Content Collections
    const slug = generateSlug(path.basename(sourcePath));
    if (slug) {
      frontmatter.slug = slug;
    }

    // Remove Jekyll-only keys
    delete frontmatter.layout;
    delete frontmatter.permalink;
    delete frontmatter.published;

    // Rewrite Liquid patterns in content
    content = rewriteLiquid(content);

    // Get output path
    const outputPath = jekyllToAstroPath(sourcePath);

    // Check for collision
    if (checkCollision(outputPath, sourcePath)) {
      return; // Skip this file
    }

    // Write migrated file
    const output = matter.stringify(content, frontmatter);
    fs.writeFileSync(outputPath, output, "utf8");

    return outputPath;
  } catch (error) {
    throw new Error(`Error migrating ${path.basename(sourcePath)}: ${error.message}`);
  }
}

/**
 * Migrate a single Jekyll page file to Astro
 */
export async function migratePageFile(sourcePath) {
  try {
    const raw = fs.readFileSync(sourcePath, "utf8");
    const parsed = matter(raw);
    const frontmatter = { ...parsed.data };
    let content = parsed.content;

    // Extract custom styles if present
    const { content: cleanContent, extractedStyles } = extractCustomStyles(content);
    content = cleanContent;

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

    // Get output path
    const outputPath = jekyllToAstroPath(sourcePath);

    // Check for collision
    if (checkCollision(outputPath, sourcePath)) {
      return; // Skip this file
    }

    // Write migrated file
    const output = matter.stringify(content, frontmatter);
    fs.writeFileSync(outputPath, output, "utf8");

    // Handle extracted styles (returned for potential aggregation)
    const result = { outputPath };
    if (extractedStyles) {
      result.extractedStyles = {
        page: path.basename(sourcePath, path.extname(sourcePath)),
        styles: extractedStyles,
      };
    }

    return result;
  } catch (error) {
    throw new Error(`Error migrating ${path.basename(sourcePath)}: ${error.message}`);
  }
}

/**
 * Delete the corresponding Astro file for a deleted Jekyll file
 */
export async function deleteAstroFile(jekyllPath) {
  try {
    const astroPath = jekyllToAstroPath(jekyllPath);

    if (fs.existsSync(astroPath)) {
      fs.unlinkSync(astroPath);
      return astroPath;
    } else {
      logger.debug(`Target file not found: ${astroPath}`);
      return null;
    }
  } catch (error) {
    throw new Error(`Error deleting ${path.basename(jekyllPath)}: ${error.message}`);
  }
}
