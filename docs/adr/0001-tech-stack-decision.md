# 1. Tech Stack Decision

Date: 2026-09-12

## Status

Accepted

## Context

The goal of this document is to provide context to the tech stack decision made during the setup of this project.

The initial setup created was co-authored by ChatGPT 5.6 Terra Light. The techstack used React + Next.js, Python + FastAPI and PostgreSQL. The initial focus was to create an MVP without getting stuck with the tech stack.

## Decision

### Backend: FastAPI

- An API framework written in Python.
- It is lighweight and unopionated.
- Does not enforce a strict project layout or built-in database ORM.
- It is becoming the industry favorite for building modern, high concurrency APIs.
- Python does better when it comes to heavy spreadsheets processing.

### Frontend: React (via Next.js)

-

### Database: PostgeSQL

- 

## Consequences

### FastAPI

- Large projects require manual architectural decisions and extra libraries.
- It does add unneccessary complexitiy for simple tasks.
