import { describe, expect, it } from 'vitest';
import { parseLocale, SUPPORTED_LOCALES } from '../src/index';

describe('SUPPORTED_LOCALES', () => {
  it('includes at least English and Spanish', () => {
    expect(SUPPORTED_LOCALES).toContain('en');
    expect(SUPPORTED_LOCALES).toContain('es');
  });
});

describe('parseLocale', () => {
  it('returns the locale for supported tags', () => {
    expect(parseLocale('fr')).toBe('fr');
  });

  it('returns null for unsupported tags', () => {
    expect(parseLocale('xx')).toBeNull();
  });
});
