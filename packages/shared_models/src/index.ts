/**
 * @annex/shared-models
 * Shared domain contracts used by web, extension, and mobile.
 * Keep this package dependency-free so every consumer can import it.
 */

/** Locale tags the ANNEX UI officially supports at launch. */
export const SUPPORTED_LOCALES = ['en', 'es', 'fr', 'de', 'hi', 'pt', 'ar', 'zh'] as const;

/** Union type of all supported locale tags. */
export type Locale = (typeof SUPPORTED_LOCALES)[number];

/**
 * Narrow a raw string to a supported Locale.
 *
 * @param value - e.g. "es"
 * @returns The Locale, or null if unsupported
 */
export function parseLocale(value: string): Locale | null {
  return (SUPPORTED_LOCALES as readonly string[]).includes(value) ? (value as Locale) : null;
}
