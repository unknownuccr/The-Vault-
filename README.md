# The Vault

A password manager built with Flask, bcrypt, and SQLite by a highschool student in about a week. 

**Last Updated Date** - 7/5/2026

**Note** - This project is not meant to be used professionally in any way. 

## Who built what

I designed and built the backend myself, the Flask routes, the SQLite schema, the
bcrypt/Fernet/PBKDF2 encryption flow, and the overall architecture. AI assisted with
parts of the frontend (templates/styling). I used AI to check for security flaws and debug things that were not working. the design decisions and the security-critical code are mine.

## How it protects your data

- **Master password** — stored only as a bcrypt hash (12 rounds). Never saved in plain form.
- **Vault entries** — encrypted at rest with Fernet (AES-128-CBC + HMAC). The encryption
  key is derived from your master password with PBKDF2-HMAC-SHA256 (600,000 iterations)
  and a per-user salt, so the key only exists in memory while you're unlocking the vault.
- **Sessions** — signed with a secret key generated on first run (stored in `.secret_key`,
  or set the `SECRET_KEY` environment variable). All forms are CSRF-protected. The session
  cookie is sent over plain HTTP by default so the local vault works out of the box; if you
  serve the vault over HTTPS, set `SESSION_COOKIE_SECURE=1` to restrict the cookie to TLS.
- **Generator** — passwords are generated in the browser with `crypto.getRandomValues`;
  they are never sent to the server.

Entries saved by older versions of this app (stored in plaintext) are automatically
re-encrypted the first time you unlock the vault.

## Running it locally

Requires Python 3.11+ and pip.

```
pip install flask bcrypt cryptography
python app.py
```

Then open `http://127.0.0.1:5000` in your browser. On first run the app creates
`.secret_key` (session signing key) and `users.db` (SQLite database) in the project
folder, both are gitignored, so they stay local to your machine.

Optional environment variables:

| Variable               | Default | What it does                                              |
| ---------------------- | ------- | ----------------------------------------------------------- |
| `SECRET_KEY`           | generated into `.secret_key` | Session signing key. Set this in production instead of relying on the file. |
| `FLASK_DEBUG`          | off     | Enables Flask's interactive debugger. **Never enable this in production** — it allows arbitrary code execution. |
| `SESSION_COOKIE_SECURE`| off     | Set to `1` if you serve the vault over HTTPS, to restrict the session cookie to TLS. |
| `VAULT_DB_PATH`        | `users.db` next to `app.py` | Overrides where the SQLite database lives. |

## Pages

| Route        | What it does                                     |
| ------------ | ------------------------------------------------ |
| `/`          | Landing page (redirects to overview if signed in) |
| `/login`     | Sign in                                          |
| `/register`  | Create an account                                |
| `/dashboard` | Overview and quick actions                       |
| `/vault`     | Unlock and view saved entries                    |
| `/vault/new` | Save a new entry                                 |
| `/generator` | Client-side password generator                   |


# things to watch for/fix
username enumeration
weak/guessable passwords (no lockout/rate limits)
logic flaws in the login/registration flow
insecure session or cookie handling

AI helped me flag some of these security flaws (username enumeration and the session/cookie handling issues in particular) during review, noted here as things to harden next.

