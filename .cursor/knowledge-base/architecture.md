# Project Rules for Firebase Functions (Python)

This guide provides specific rules and best practices for developing, testing, and deploying serverless functions on Firebase using the Python runtime. You are an expert in creating robust, scalable, and secure Cloud Functions.

## 🏛️ Core Architecture & Design

-   **Single Responsibility**: Each function should perform **one logical task**. A function named `onUserCreate` should only handle user creation logic, not send welcome emails and process images. Chain functions for multi-step workflows.
-   **Idempotency**: Design background-triggered functions (e.g., Firestore, Pub/Sub) to be **idempotent**. This means running a function multiple times with the same input data will not result in errors or duplicate data.
-   **Function Types**: Be explicit about the function type you are writing (HTTP, Callable, Firestore Trigger, etc.) and follow the best practices for each.

---

## 🏗️ Project & Code Structure

-   **Standard Directory Structure**: All Python code for your functions **must** reside within a dedicated `functions` directory at the root of your Firebase project. The Firebase CLI expects this structure.
    ```
    /my-firebase-project
    ├── firebase.json
    ├── .firebaserc
    └── functions/          <-- YOUR PYTHON CODE GOES HERE
        ├── main.py
        ├── requirements.txt
        └── ... (other python files)
    ```
-   **File Organization (Single vs. Multiple Files)**:
    -   Firebase, by default, looks for all your function triggers in the `main.py` file.
    -   For small projects (1-5 functions), defining them all in `main.py` is acceptable.
    -   For larger projects, **you should split your code into multiple files/modules** by feature (e.g., `api/users.py`, `triggers/storage.py`). Then, import these functions into `main.py` to expose them to Firebase for deployment. Your `main.py` acts as an index file.

    **Example Structure:**
    ```
    functions/
    ├── main.py
    ├── requirements.txt
    ├── api/
    │   ├── __init__.py
    │   └── users.py
    └── triggers/
        ├── __init__.py
        └── firestore.py
    ```
    **Example `main.py`:**
    ```python
    # main.py - Acts as the entry point
    import firebase_admin

    # Import functions from other files to register them
    from api.users import get_user_profile
    from triggers.firestore import on_document_write

    firebase_admin.initialize_app()

    # The imported names are now available for deployment
    # firebase deploy --only functions:get_user_profile,functions:on_document_write
    ```

---

## ⚙️ Implementation & Configuration

-   **Explicitly Set the Region**: **Always** specify the deployment region in the function's decorator. This ensures your functions are co-located with your other Firebase services (like Firestore and Storage), minimizing latency and network costs.
    ```python
    from firebase_functions import https_fn, options

    # Set the region for all functions in the file
    options.set_global_options(region="europe-west1")

    # Or set it per function
    @https_fn.on_request(region="europe-west1")
    def my_http_function(req: https_fn.Request) -> https_fn.Response:
        # ...
    ```
-   **SDK Initialization**: Initialize the Firebase Admin SDK **once per instance**. Declare `firebase_admin.initialize_app()` in the global scope of your `main.py`.
-   **Dependencies**: All dependencies must be listed in the `functions/requirements.txt` file.
-   **Environment & Secrets**:
    -   **NEVER** hardcode API keys or sensitive data.
    -   Use Firebase's built-in environment configuration (`firebase functions:config:set`) or Secret Manager.
-   **Logging**: Use the standard Python `logging` library. Firebase automatically routes logs to Google Cloud Logging.

---

## ⚡ Performance & Optimization

-   **Cold Starts**: Be aware of cold starts. Use global variables to cache objects (like database clients) that can be reused between invocations.
-   **Resource Management**: Configure function resources (memory, timeout, min/max instances) appropriately. Start with defaults and adjust based on monitoring.
-   **Background Functions**: For long-running tasks, use background-triggered functions instead of HTTP functions to avoid client timeouts.

---

## 🛡️ Security

-   **Input Validation**: **ALWAYS** validate incoming data, especially for HTTP and Callable functions. Use a library like Pydantic to define and enforce data schemas.
-   **Authentication & Authorization**: For HTTP functions, verify the user's identity by validating the Firebase Auth ID Token.

---

## 🧪 Testing & Deployment

-   **Local Testing**: **Crucially, use the Firebase Local Emulator Suite** (`firebase emulators:start`). This is the most effective way to test your functions, triggers, and security rules locally.
-   **Unit Tests**: Write unit tests for your core business logic, mocking the Firebase Admin SDK.
-   **Deployment**: Deploy only the functions you've changed using the Firebase CLI:
    `firebase deploy --only functions:myFunction1,functions:myFunction2`