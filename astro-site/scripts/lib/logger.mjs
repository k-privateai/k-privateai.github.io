import chalk from "chalk";

/**
 * Get current timestamp in HH:MM:SS format
 */
function getTimestamp() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
  const seconds = String(now.getSeconds()).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

/**
 * Log levels
 */
export const LOG_LEVELS = {
  DEBUG: "DEBUG",
  INFO: "INFO",
  WARN: "WARN",
  ERROR: "ERROR",
};

/**
 * Logger class with colored output
 */
export class Logger {
  constructor(prefix = "WATCH") {
    this.prefix = prefix;
  }

  /**
   * Format log message with timestamp and prefix
   */
  _format(level, message) {
    const timestamp = chalk.gray(`[${getTimestamp()}]`);
    const prefixText = chalk.bold(`[${this.prefix}]`);
    return `${timestamp} ${prefixText} ${message}`;
  }

  /**
   * Log info message (green checkmark)
   */
  info(message) {
    console.log(this._format(LOG_LEVELS.INFO, chalk.green(`✅ ${message}`)));
  }

  /**
   * Log success message (green)
   */
  success(message) {
    console.log(this._format(LOG_LEVELS.INFO, chalk.green(message)));
  }

  /**
   * Log warning message (yellow warning sign)
   */
  warn(message) {
    console.log(this._format(LOG_LEVELS.WARN, chalk.yellow(`⚠️  ${message}`)));
  }

  /**
   * Log error message (red X)
   */
  error(message, error = null) {
    console.error(this._format(LOG_LEVELS.ERROR, chalk.red(`❌ ${message}`)));
    if (error && error.stack) {
      console.error(chalk.gray(error.stack));
    }
  }

  /**
   * Log delete operation (trash icon)
   */
  delete(message) {
    console.log(this._format(LOG_LEVELS.INFO, chalk.magenta(`🗑️  ${message}`)));
  }

  /**
   * Log stats message (cyan)
   */
  stats(message) {
    console.log(this._format(LOG_LEVELS.INFO, chalk.cyan(message)));
  }

  /**
   * Log debug message (gray, only if DEBUG env var is set)
   */
  debug(message) {
    if (process.env.DEBUG) {
      console.log(this._format(LOG_LEVELS.DEBUG, chalk.gray(message)));
    }
  }
}

/**
 * Default logger instance
 */
export const logger = new Logger("WATCH");
