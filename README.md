# 🏦 Uniccon Loan Approval Bot

A Streamlit web app that provides an AI-powered assistant for analyzing loan applications and surfacing historical loan approval patterns.

This repository is intended for data-driven loan guidance. It combines a simple dataset-backed analysis pipeline with optional local LLM integration (Ollama) for conversational assistance.

## Quick overview

- Web UI: `app.py` (Streamlit)
- Core modules: `modules/` containing data loading, model handling (Ollama), chat engine, and UI helpers
- Data: `loan_data.csv` (expected columns described below)
- Tests: `test_imports.py`, `test_fixed.py` (lightweight smoke tests)

## Prerequisites

1. Python 3.8 or newer
2. pip (or your preferred Python package manager)
3. (Optional for LLM features) Ollama installed locally and a local Llama2 model in Ollama

If you don't have Ollama or a local model, the code provides deterministic fallback responses so the app will still run (with reduced AI features).

## Install dependencies

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

The main dependencies are Streamlit, pandas, scikit-learn, plotly and `ollama` (optional for LLM).

## Run the app (development)

From the project root run (Windows PowerShell):

```powershell
streamlit run app.py
```

There are helper batch files in the repo root (`run_app.bat`, `start_app.bat`) you can use on Windows.

## Project architecture and important patterns

The app separates concerns into lightweight modules under `modules/`:

- `modules/data_loader.py` — `LoanDataLoader(file_path)`
  - Responsible for reading `loan_data.csv`, preprocessing, and computing dataset statistics.
  - Public API used elsewhere: `load_data()`, `preprocess_data()`, `get_approval_stats()`, `get_sample_data()`.

- `modules/model_handler.py` — `LoanApprovalModel(model_name)`
  - Wraps Ollama model calls and handles model availability detection.
  - Key methods: `initialize_model()`, `generate_response(prompt, context="")`, `analyze_loan_application(data)`.
  - If Ollama is unreachable, the class returns deterministic fallback responses — preserve that behavior when changing the module.

- `modules/chat_engine.py` — `LoanApprovalChatEngine(data_file_path)`
  - Composes `LoanDataLoader` and `LoanApprovalModel` to provide chat behavior and application analysis.
  - Builds a `data_context` from `get_approval_stats()` and passes it to `model.generate_response(...)`.
  - Public methods used by the UI: `process_message(user_message)`, `get_approval_analysis(user_data)`, `clear_history()`.

- `modules/utils.py` — UI helpers (Streamlit charts, validation, logging setup).

Why these decisions matter (important for contributors and AI agents):

- LLM integration is optional. Keep graceful degradation. Changes to the model calling pattern must preserve the `model_available` check and fallback path.
- The chat engine constructs a `data_context` string used for prompt context. Modifying this format will change what the model sees.
- Streamlit state keys are relied on across files: `st.session_state.chat_engine`, `st.session_state.data_loader`, `st.session_state.df`, `st.session_state.messages`. Avoid renaming these keys without migrating other code.

## Data format (`loan_data.csv`)

The app expects a CSV with at least the following columns (case-sensitive):

- `Approval` — values like `Approved` / `Rejected`
- `Income` — numeric annual income
- `Credit_Score` — numeric credit score (300–850)
- `Loan_Amount` — numeric loan requested
- `DTI_Ratio` — numeric debt-to-income percentage
- `Employment_Status` — `employed` / `unemployed` (or similar)

`LoanDataLoader.preprocess_data()` will create derived fields used in UI and analysis:

- `Approval_Binary`, `Employment_Status_Binary`, `Loan_to_Income_Ratio`, `Credit_Score_Group`

If your CSV differs, adapt either the CSV or `data_loader.py` and keep the derived field names stable where other modules reference them.

## Streamlit UI flow and session state

- `app.py` initializes and stores objects in `st.session_state`:
  - `st.session_state.chat_engine` — `LoanApprovalChatEngine` instance (may be `None` on errors)
  - `st.session_state.data_loader` — `LoanDataLoader` instance
  - `st.session_state.df` — loaded DataFrame
  - `st.session_state.stats` — approval stats dict
  - `st.session_state.messages` — chat history list of dicts with `role` and `content`

- UI pages:
  - Chat with Bot — uses `chat_engine.process_message()` for conversational responses
  - Data Analysis — visualizations and stats from `data_loader`
  - Loan Application Analysis — collects user input and calls `chat_engine.get_approval_analysis()`

When editing UI code, maintain these keys and shapes to avoid runtime errors.

## Model integration and fallbacks

- `LoanApprovalModel` calls `ollama.list()` during initialization to detect availability. If that call fails, `model_available` is set to `False` and fallback methods (`_get_fallback_response`, `_get_fallback_analysis`) are used.
- Preserve low temperature / deterministic options when calling a model (current code uses `temperature: 0.1`) if you change prompt construction.

## Running the quick checks

Two simple smoke scripts are provided.

- Import test:

```powershell
python test_imports.py
```

- Full smoke test:

```powershell
python test_fixed.py
```

These scripts exercise basic imports, data loading and model initialization; they are useful after changing module APIs.

## Development notes and conventions

- Preserve public module APIs (listed above). Avoid breaking changes without updating the UI and tests.
- Favor safe fallbacks over raising exceptions for missing external systems (Ollama, data files).
- Keep changes small and run the smoke tests before submitting PRs.

Suggested small improvements that are safe to add:

- Add unit tests for `LoanDataLoader.preprocess_data()` and `get_approval_stats()`.
- Add a small integration test that runs `LoanApprovalChatEngine` with a mocked `LoanApprovalModel` to validate the chat flow.

## Troubleshooting

- If the app fails to start because `loan_data.csv` is missing: place your CSV in the project root or update the path in `app.py`/`LoanDataLoader`.
- If Ollama calls fail: ensure Ollama is installed and running locally. The app will continue to run using fallbacks, but AI answers will be limited.

## Contributing

Please open issues or PRs. For code changes, run the smoke tests and include any relevant data or model notes.

---

If something about the setup, data format, or LLM integration is missing or you'd like a shorter quickstart targeted to a specific OS, tell me which parts to expand and I'll update this README.
# 🏦 Uniccon Loan Approval Bot

An AI-powered chatbot for loan approval analysis using LangChain, Ollama, and Streamlit.

## Prerequisites

1. **Python 3.8+**
2. **Ollama** installed locally
3. **Llama2 model** downloaded in Ollama

## Installation

1. **Install Ollama**:
   ```bash
   # On macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # On Windows, download from https://ollama.ai/