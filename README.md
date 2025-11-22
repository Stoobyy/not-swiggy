# Not-Swiggy - A CLI Based Food Ordering System

A simple command-line DBMS project built in Python for managing restaurant orders, users, and payments — all using MySQL as the backend.

---

##  Features

- User registration and login with encrypted passwords  
- Restaurant listing and menu browsing  
- Order placement with real-time cart system  
- Payment handling (cash or saved card)  
- View previous orders with delivery time estimation  
- Change password and manage saved cards  

---

##  Project Structure

```
│
├── main.py          # CLI application (entry point)
├── db/
│   ├── setup.py     # Database setup and initial data insertion
│   └── sql.py       # Database operations (user, orders, payment)
├── sqlDetails.json  # Generated during setup (stores DB credentials)
├── .env             # Contains encryption key (FERNET_KEY)
```

---

##  Setup Instructions

1. **Run setup script**
   ```bash
   python db/setup.py
   ```
   - Enter your MySQL host, username, and password.
   - This creates the `yippee` database with required tables and sample restaurant data.

2. **Add encryption key**
   Create a file named `.env` in the root directory:
   ```
   FERNET_KEY=<your_generated_key>
   ```
   To generate one:
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

3. **Run the main program**
   ```bash
   python -m app.main
   ```

---

##  Tech Stack

- **Python 3**
- **MySQL**
- **Rich** - for styled CLI interface  
- **Cryptography (Fernet)** - for secure password & payment encryption  
- **Humanize** - for readable delivery time display  
- **pwinput** - for hidden password input  

---

##  Why No Front End?

Because we were lazy.
And honestly, the terminal is kind of beautiful when it works.
Plus, we just wanted to focus on the database logic - the “DB” part of DBMS - and not fight with HTML and CSS.

---

##  License

This project is open for educational and academic use.
