import chokidar from "chokidar";
import path from "path";
import { fileURLToPath } from "url";
import { logger } from "./lib/logger.mjs";
import {
  ensureDirectories,
  migratePostFile,
  migratePageFile,
  deleteAstroFile,
} from "./lib/migrator.mjs";
import { getFileType, getRelativePath, DIRS } from "./lib/file-mapper.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Ensure output directories exist
ensureDirectories();

// Batch processing state
let pendingFiles = new Map();
let batchTimer = null;
const BATCH_DELAY = 500; // 500ms debounce

/**
 * Process a single file change event
 */
async function processFile(eventType, filePath) {
  const relativePath = getRelativePath(filePath);
  const fileType = getFileType(filePath);

  try {
    if (eventType === "unlink") {
      // Handle file deletion
      const deletedPath = await deleteAstroFile(filePath);
      if (deletedPath) {
        logger.delete(`${relativePath} → ${path.basename(deletedPath)}`);
      }
    } else {
      // Handle file addition or change
      let result;
      if (fileType === "post") {
        result = await migratePostFile(filePath);
        if (result) {
          logger.info(`${relativePath} → ${path.basename(result)}`);
        }
      } else if (fileType === "page") {
        result = await migratePageFile(filePath);
        if (result && result.outputPath) {
          logger.info(`${relativePath} → ${path.basename(result.outputPath)}`);
          if (result.extractedStyles) {
            logger.debug(`Extracted styles from ${result.extractedStyles.page}`);
          }
        }
      } else {
        logger.warn(`Unknown file type: ${relativePath}`);
      }
    }
  } catch (error) {
    logger.error(`Failed to process ${relativePath}`, error);
  }
}

/**
 * Process batch of pending files
 */
async function processBatch() {
  if (pendingFiles.size === 0) return;

  const startTime = Date.now();
  const files = Array.from(pendingFiles.entries());
  pendingFiles.clear();

  logger.stats(`Processing ${files.length} file(s)...`);

  for (const [filePath, eventType] of files) {
    await processFile(eventType, filePath);
  }

  const duration = Date.now() - startTime;
  logger.stats(`Processed ${files.length} file(s) in ${duration}ms`);
}

/**
 * Queue file for batch processing
 */
function queueFile(eventType, filePath) {
  pendingFiles.set(filePath, eventType);

  clearTimeout(batchTimer);
  batchTimer = setTimeout(() => {
    processBatch();
  }, BATCH_DELAY);
}

/**
 * Initialize file watcher
 */
function startWatcher() {
  logger.success("Starting Jekyll to Astro file watcher...");
  logger.info(`Watching: _posts/, _pages/`);
  logger.info(`Target: astro-site/src/`);
  logger.info("Press Ctrl+C to stop\n");

  const watcher = chokidar.watch(
    ["_posts/**/*.{md,markdown}", "_pages/**/*.{md,markdown,html}"],
    {
      persistent: true,
      ignoreInitial: true, // Don't trigger on startup (use migrate:all for initial sync)
      awaitWriteFinish: {
        stabilityThreshold: 300, // Wait 300ms for file write to finish
        pollInterval: 100,
      },
      ignored: ["**/node_modules/**", "**/.git/**", "**/.*"],
      cwd: DIRS.PROJECT_ROOT,
    }
  );

  watcher
    .on("add", (filePath) => {
      const absPath = path.join(DIRS.PROJECT_ROOT, filePath);
      queueFile("add", absPath);
    })
    .on("change", (filePath) => {
      const absPath = path.join(DIRS.PROJECT_ROOT, filePath);
      queueFile("change", absPath);
    })
    .on("unlink", (filePath) => {
      const absPath = path.join(DIRS.PROJECT_ROOT, filePath);
      queueFile("unlink", absPath);
    })
    .on("error", (error) => {
      logger.error("Watcher error", error);
    })
    .on("ready", () => {
      logger.success("File watcher ready!");
      logger.info("Waiting for changes...\n");
    });

  // Graceful shutdown
  process.on("SIGINT", () => {
    logger.info("\nShutting down file watcher...");
    watcher.close();
    process.exit(0);
  });

  process.on("SIGTERM", () => {
    logger.info("\nShutting down file watcher...");
    watcher.close();
    process.exit(0);
  });

  // Handle uncaught errors
  process.on("uncaughtException", (error) => {
    logger.error("Uncaught exception", error);
    // Don't exit - keep watching
  });

  process.on("unhandledRejection", (reason, promise) => {
    logger.error("Unhandled promise rejection", reason);
    // Don't exit - keep watching
  });

  return watcher;
}

// Start the watcher
startWatcher();
