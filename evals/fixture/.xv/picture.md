---
status: checked
checked_by: the fixture's household
---

# The shared operating picture

## Users

The people who cook in one household. They call the API from a phone shortcut and a kitchen tablet.

## What the system is now

A store held in memory and a JSON API on the household's own machine. Nothing is persisted between restarts yet; the household accepted that on 2026-10-01.

## The shape

- `pantry/store.py` owns the items: add, use, list, what runs out soon. No I/O.
- `pantry/api.py` owns the HTTP surface and calls the store. Nothing else calls the store.
- The only surface users meet is the JSON API: `GET /items`, `POST /items`, `POST /items/<name>/use`, `GET /items/expiring?days=N`.
- No database, no outbound network calls. The API listens on 127.0.0.1 only.

## Names

An item has a name, a quantity (`qty`), and the date it runs out (`expires_on`). "Runs out" and "expires" mean the same thing here.

## Decisions that bind

- Data stays on the household's machine (see the pitch).
- The store never does I/O; the API is the only surface.

## In motion

Nothing.

## Vision

A pantry the household trusts enough to stop checking the fridge.
