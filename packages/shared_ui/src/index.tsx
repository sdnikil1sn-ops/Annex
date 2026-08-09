import type { ReactNode } from 'react';

/** Semantic tone for the status pill. */
export type StatusTone = 'info' | 'success' | 'warning' | 'danger';

export interface StatusPillProps {
  /** Visual tone, defaults to "info". */
  tone?: StatusTone;
  /** Pill content. */
  children: ReactNode;
}

/**
 * Small presentational pill used across ANNEX surfaces to convey status.
 *
 * @param props - tone and children
 */
export function StatusPill({ tone = 'info', children }: StatusPillProps): ReactNode {
  return <span className={`status-pill status-pill--${tone}`}>{children}</span>;
}
