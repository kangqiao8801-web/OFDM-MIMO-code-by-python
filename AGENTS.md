# Project Rules

## Goal
- Convert the MATLAB programs in `MIMO-OFDM无线通信技术及MATLAB实现SourceCode  /` to Python one by one.
- Each converted Python program must run successfully and save its expected figures or numerical results.

## Source Policy
- Treat the original MATLAB source directory as read-only reference material.
- Do not rename, move, reformat, or edit original `.m` and `.dat` files unless explicitly requested.

## Python Runtime
- Use `/opt/homebrew/bin/python3.12` for all Python commands.
- Use `uv` to manage the project `.venv`.
- Keep converted shared code in `src/ofdm_mimo/`.
- Keep runnable converted scripts in `examples/`.
- Save generated figures, `.dat` files, and logs under `outputs/`.

## Development Flow
- Default to TDD: add or update tests first, then implement until they pass.
- Keep conversions numerically faithful to the MATLAB algorithm and variable meaning, while using natural Python and NumPy style.
- Use fixed random seeds in runnable examples so results are reproducible.
- After changes, run `/opt/homebrew/bin/python3.12 -m pytest` from the activated project environment or `.venv/bin/python -m pytest`.
