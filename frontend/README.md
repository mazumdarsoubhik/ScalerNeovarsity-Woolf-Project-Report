## NutriFlow Frontend (Streamlit)

Single-app Streamlit UI integrated with backend APIs:
- `Today` tab for meal logging and dashboard
- `History` tab for filtered meal history and edit/delete
- `Chat` tab for nutrition assistant
- `Settings` tab for backend URL + logout
- Auth screen for email/password login or registration

### Run

From `frontend/`:

```bash
py -3 -m pip install -r requirements.txt
py -3 -m streamlit run app.py
```

Compatibility entrypoint (also works):

```bash
py -3 -m streamlit run streamlit-app.py
```
