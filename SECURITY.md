# Security Policy

ANNEX takes security seriously. This platform analyzes media and information —
integrity and trustworthiness are core product requirements.

## Reporting a vulnerability

**Do not open a public issue.** Report privately to security@annex.dev.

Please include:
- Affected component(s) and version(s)
- Steps to reproduce
- Impact assessment
- Any proposed fix

You should receive a response within 48 hours. If the issue is confirmed, a fix
is coordinated and a security advisory is published via GitHub.

## Scope

In scope: the code in this repository, our CI/CD configuration, and our
deployment manifests. Out of scope: third-party services (Supabase, Firebase,
OpenAI, Gemini) and their own infrastructure.

## Security principles

- Secrets never in code — only in environment variables or secret managers.
- All API endpoints validate input and enforce rate limits.
- Authentication via Firebase Auth; authorization enforced per route.
- Prompt injection, XSS, CSRF, and SQL injection are treated as release-blocking.

## Supported versions

Only the latest tagged release receives security fixes. Pre-release (`0.x`)
versions receive fixes on `main` and are backported on a best-effort basis.
