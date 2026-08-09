import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';
import { StatusPill } from '../src/index';

describe('StatusPill', () => {
  it('renders children with the tone class', () => {
    const html = renderToStaticMarkup(<StatusPill tone="success">Verified</StatusPill>);
    expect(html).toContain('status-pill--success');
    expect(html).toContain('Verified');
  });

  it('defaults to the info tone', () => {
    const html = renderToStaticMarkup(<StatusPill>Info</StatusPill>);
    expect(html).toContain('status-pill--info');
  });
});
