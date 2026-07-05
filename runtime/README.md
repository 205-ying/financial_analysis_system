# Runtime Files

`runtime/` is the local runtime boundary for generated files that should not live
inside source directories or be committed to Git.

Recommended layout:

```text
runtime/
├─ logs/
│  └─ api/                 # FastAPI application logs and rotated archives
│     └─ test-runs/        # Local test, lint, and diagnostic logs
├─ uploads/
│  └─ imports/             # Uploaded import source files and error reports
├─ test-results/
│  └─ api/                 # Backend coverage reports and test artifacts
└─ tmp/                    # Disposable local scratch files
```

Only this README and `.gitignore` are tracked. Generated files under this
directory are intentionally ignored.
