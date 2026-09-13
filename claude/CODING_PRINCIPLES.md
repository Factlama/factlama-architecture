# Coding principles

Implement a small end-to-end slice with deterministic fixtures before expanding abstractions. Validate inputs and bound external calls. Make failure, absence and abstention explicit. Preserve provenance and correlation IDs. Use metadata-only capture by default and redact before persistence or logging. Prefer simple, inspectable storage/queue choices for the local MVP; introduce distributed infrastructure only after measured need. Keep contract fixtures identical across repositories.
