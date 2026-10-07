# Orchestrator Skills

## Workflow
1. Understand the target company/product.
2. Search when category context is needed.
3. Identify exactly three meaningful direct or strategic competitors.
4. Exclude the target.
5. Return JSON only.

## Output
```json
{"competitors": ["Competitor 1", "Competitor 2", "Competitor 3"]}
```

## Edge cases
- Prefer direct alternatives over vague adjacent companies.
- Resolve ambiguous company/product names with search.
- Never return fewer or more than three.
