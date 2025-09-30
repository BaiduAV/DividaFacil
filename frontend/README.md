
  # Expenses Splitter App Layout

  This is a code bundle for Expenses Splitter App Layout. The original project is available at https://www.figma.com/design/SQzau4n7YQwMhB8Tg6Lq2G/Expenses-Splitter-App-Layout.

  ## Running the code

  Run `npm i` to install the dependencies.

  Run `npm run dev` to start the development server.
  
  ## Authentication Flow

  The frontend now bootstraps authentication state using the `/api/session` endpoint instead of calling `/api/users` (which requires prior authentication and returned an array with only the current user).

  1. On app mount, `AuthContext` calls `GET /api/session`.
  2. If `{ authenticated: true }`, it stores the returned user object.
  3. Login (`POST /api/login`) and signup (`POST /api/signup`) set the session cookie; the context then re-runs the session check.
  4. A global `api:unauthorized` browser event is dispatched whenever a 401 response is received, allowing listeners to react (e.g., force logout UI).

  ### Session Response Shape
  ```json
  { "authenticated": true, "user": { "id": "...", "name": "...", "email": "..." } }
  ```
  or
  ```json
  { "authenticated": false }
  ```

  ### Why this change?
  - Avoids initial 401 errors during unauthenticated page loads.
  - Clarifies intent: a lightweight status check instead of a user list endpoint that exposed only the current user.
  - Simplifies future extension (e.g., session expiry, roles) without changing consumer code.
  