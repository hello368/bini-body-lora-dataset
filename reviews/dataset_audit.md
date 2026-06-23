# Bini Body Dataset Audit

Generated: 2026-06-23T00:40:45

## Summary

- `selected`: 100 images, 100 caption files
- `gold`: 0 images, 0 caption files
- `needs_fix`: 5 images, 5 caption files
- `rejected`: 23 images, 23 caption files

## Review Status Counts

- `needs_fix`: 5
- `rejected`: 23
- `selected`: 100

## Errors

- None

## Warnings

- None

## Production Rule

Train body LoRA only from `datasets/bini_body_selected/` or manually promoted `datasets/bini_body_gold/`.
Never train from `datasets/bini_body_needs_fix/`, `datasets/bini_body_rejected/`, `needs_fix/`, or `rejected/`.
Use `bk_bini_body` as the body trigger. Keep `bk_bini_teen` for the separate face LoRA only.
