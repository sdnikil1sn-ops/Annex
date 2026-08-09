import { describe, expect, it } from 'vitest';
import { slugify } from '../src/index';

describe('slugify', () => {
  it('lowercases and trims whitespace', () => {
    expect(slugify('  Media Literacy  ')).toBe('media-literacy');
  });

  it('strips accents and handles punctuation', () => {
    expect(slugify('¿Qué es la desinformación?')).toBe('que-es-la-desinformacion');
  });

  it('handles multiple separators', () => {
    expect(slugify('A  B___C')).toBe('a-b-c');
  });
});
