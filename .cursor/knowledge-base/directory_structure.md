# Current Directory Structure

## Core Components

```
.
- **api_docs/**
    - **Chome Firebase Function/**
        - bruno.json
        - duplicate event.bru
        - **environments/**
            - ChomeFirebaseFunctionDev.bru
- firebase.json
- firestore.indexes.json
- firestore.rules
- **functions/**
    - .gitignore
    - main.py
    - requirements.txt
    - setup.py
    - **src/**
        - **auth/**
            - auth_service.py
            - __init__.py
        - **config/**
            - __init__.py
            - settings.py
        - **email/**
            - email_service.py
            - __init__.py
        - **events/**
            - event_service.py
            - __init__.py
        - __init__.py
        - main.py
        - **reservations/**
            - __init__.py
            - reservation_service.py
        - **utils/**
            - firestore_client.py
            - __init__.py
            - logging.py
    - test_env.py
    - test_import.py
    - **tests/**
        - __init__.py
        - test_auth.py
- .gitignore
- README.md
- REFACTORING_SUMMARY.md
- storage.rules
```
