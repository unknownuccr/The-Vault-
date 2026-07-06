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


# AI use in this project

- While I normally code by hand to help expand my knowledge of how things work, I did not want to spend an extended period of time learning a foreign topic that would increase the timeframe of this project outside of the summer months. For that reason, AI was particularly useful in this project with some advanced topics that were a little out of reach for my current knowledge. 

- **How I Worked With AI** - Throughout the project, I tried my hardest not to rely on AI as a crutch. My workflow would include me implementing what I knew and then have AI fill in the rest. ex. I would implement code by hand to the best of my ability -----> anytime I ran into something I did not fully know how to do I would turn to AI to help me understand and to teach me ------> if the logic was too hard to learn in the next day or two I would then have AI implement it for me and explain what it did ------> I would take a mental note of it for things to learn in the future and move on. 

- Uses of AI to code or teach in this project include: 
    - Advanced HTML design
    - Security planning and hardening 
    - The implementation of the Base64 logic that can be found in 'crypto.py'
    - The CSS stylesheet in '/static/css/style.css'
    - Used to help me understand how SQLite and Flask worked which would later be coded by me 
    - Most all of the Javascript logic found in '/static/js/app.js'
    - Favicon Generation found in '/static/favicon.svg'

- I found the backend to be easier as it was the part of the project where I used AI the least. The frontend implementation was quite difficult because I had never worked with HTML or CSS before. A large majority of my AI use was on the frontend. 

# Planned to Add
- Email setup and actual account recovery.
- 2FA for further protection.
- Alerts to know when your password appears in a data leak. 
- A tool that checks to see if an entered password has appeared in a data leak. 
- Making the project a real web app and an iOS app.
- An IDS/Intrusion Detection System.  
    