import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Base directories
const PROJECT_ROOT = path.join(__dirname, "../../../");
const JEKYLL_POSTS_DIR = path.join(PROJECT_ROOT, "_posts");
const JEKYLL_PAGES_DIR = path.join(PROJECT_ROOT, "_pages");
const JEKYLL_DATA_DIR = path.join(PROJECT_ROOT, "_data");
const ASTRO_POSTS_DIR = path.join(__dirname, "../../src/content/posts");
const ASTRO_PAGES_DIR = path.join(__dirname, "../../src/pages");
const ASTRO_DATA_DIR = path.join(__dirname, "../../src/data");

/**
 * Generate a clean slug from filename
 * Removes date and timezone prefix, converts to lowercase kebab-case
 */
export function generateSlug(filename) {
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
 * Determine file type from path
 */
export function getFileType(sourcePath) {
  const normalized = path.normalize(sourcePath);

  if (normalized.includes("_posts")) {
    return "post";
  } else if (normalized.includes("_pages")) {
    return "page";
  } else if (normalized.includes("_data")) {
    return "data";
  }

  return "unknown";
}

/**
 * Convert Jekyll post path to Astro path
 * Example: _posts/2024-10-07-PDT - K-PAI.markdown → src/content/posts/k-pai-seminar.md
 */
export function jekyllPostToAstroPath(jekyllPath) {
  const slug = generateSlug(jekyllPath);
  const outputFilename = slug ? `${slug}.md` : path.basename(jekyllPath).replace('.markdown', '.md');
  return path.join(ASTRO_POSTS_DIR, outputFilename);
}

/**
 * Convert Jekyll page path to Astro path
 * Example: _pages/about.md → src/pages/about.md
 */
export function jekyllPageToAstroPath(jekyllPath) {
  const basename = path.basename(jekyllPath);
  // Convert .markdown to .md for consistency
  const filename = basename.replace('.markdown', '.md');
  return path.join(ASTRO_PAGES_DIR, filename);
}

/**
 * Convert Jekyll data path to Astro path
 * Example: _data/navigation.yml → src/data/navigation.json
 */
export function jekyllDataToAstroPath(jekyllPath) {
  const basename = path.basename(jekyllPath);
  // Convert .yml/.yaml to .json
  const filename = basename.replace(/\.(yml|yaml)$/, '.json');
  return path.join(ASTRO_DATA_DIR, filename);
}

/**
 * Convert Jekyll path to corresponding Astro path
 */
export function jekyllToAstroPath(jekyllPath) {
  const fileType = getFileType(jekyllPath);

  switch (fileType) {
    case "post":
      return jekyllPostToAstroPath(jekyllPath);
    case "page":
      return jekyllPageToAstroPath(jekyllPath);
    case "data":
      return jekyllDataToAstroPath(jekyllPath);
    default:
      throw new Error(`Unknown file type for path: ${jekyllPath}`);
  }
}

/**
 * Get relative path from project root
 */
export function getRelativePath(absolutePath) {
  return path.relative(PROJECT_ROOT, absolutePath);
}

/**
 * Export directory constants
 */
export const DIRS = {
  PROJECT_ROOT,
  JEKYLL_POSTS_DIR,
  JEKYLL_PAGES_DIR,
  JEKYLL_DATA_DIR,
  ASTRO_POSTS_DIR,
  ASTRO_PAGES_DIR,
  ASTRO_DATA_DIR,
};
