# The Vault

A password manager built with Flask, bcrypt, and SQLite. 

**Last Updated Date** - 7/5/2026

**Note** - This project is not meant to be used professionally in any way. 

## How it protects your data

- **Master password** — stored only as a bcrypt hash (12 rounds). Never saved in plain form.
- **Vault entries** — encrypted at rest with Fernet (AES-128-CBC + HMAC). The encryption
  key is derived from your master password with PBKDF2-HMAC-SHA256 (600,000 iterations)
  and a per-user salt, so the key only exists in memory while you're unlocking the vault.
- **Sessions** — signed with a secret key generated on first run (stored in `.secret_key`,
  or set the `SECRET_KEY` environment variable). All forms are CSRF-protected.
- **Generator** — passwords are generated in the browser with `crypto.getRandomValues`;
  they are never sent to the server.

Entries saved by older versions of this app (stored in plaintext) are automatically
re-encrypted the first time you unlock the vault.

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


