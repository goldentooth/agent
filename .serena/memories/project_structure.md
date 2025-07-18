# Project Structure

## Root Directory Layout
```
agent/
├── main.py              # Entry point with basic print statement
├── pyproject.toml       # Project configuration (Python 3.11+, no deps)
├── README.md           # Basic project description
├── LICENSE             # Unlicense (public domain)
├── .python-version     # Python 3.11
├── .gitignore          # Comprehensive Python gitignore
├── CLAUDE.md           # Claude Code assistant instructions
├── .emoji              # Project emoji file
└── .serena/            # Serena agent configuration
    ├── project.yml
    └── memories/
```

## Key Files
- `main.py`: Simple entry point with main() function
- `pyproject.toml`: Minimal project config, no dependencies
- No source code directories (src/, lib/, etc.) yet
- No test directories or files