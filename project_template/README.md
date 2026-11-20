# New client project template

This folder is a starting point, **not** a complete report. It is copied into each new client folder, away from the toolkit source.

1. Copy the **contents** of `project_template/` into the client's new folder.
2. Create a separate client `.venv` in PyCharm.
3. Install the central toolkit, using the client's own interpreter:
   ```powershell
   .\.venv\Scripts\python.exe -m pip install -e "C:\path\to\caelik-freelance-toolkit"
   ```
4. Keep untouched original files in `data/raw/`, separate from generated files in `output/`.
5. The minimal `main.py` expects one file named `source.xlsx`; adjust this to match the actual client.
6. For multiple source files or sheets, load each as a separate DataFrame:

   ```python
   from caelik_toolkit import load_table

   sales = load_table(RAW / "pos.csv")
   products = load_table(RAW / "inventory.xlsx", sheet_name="Product List")
   stock = load_table(RAW / "inventory.xlsx", sheet_name="Stock Count")
   ```

7. Place client-approved business mappings, refunds, exception rules, and corrections in `project_rules.py`.
8. Reconcile totals, check original-source preservation, and only then produce the client-facing deliverable.

Never modify the original source files. Don't copy private client data into the central toolkit project or its Git repository.
