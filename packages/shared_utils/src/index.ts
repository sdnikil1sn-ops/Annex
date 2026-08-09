/**
 * @annex/shared-utils
 * Framework-agnostic utility functions shared across ANNEX apps (web, extension, mobile).
 */

/**
 * Convert any string into a URL/route-safe slug.
 *
 * @param input - Raw string, e.g. "¿Qué es la desinformación?"
 * @returns A lowercase ASCII slug, e.g. "que-es-la-desinformacion"
 */
export function slugify(input: string): string {
  return input
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
