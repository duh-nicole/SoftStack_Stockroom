# ☕ SoftStack Stockroom — Full-Stack Inventory API & Dashboard

A lightweight, full-stack inventory management system built with a **FastAPI** backend, **SQLite** database, and an
interactive **Vanilla JavaScript** frontend featuring custom theme switching and secure JWT authentication.

![SoftStack Stockroom Dashboard](./Stockroom_Product_List.png)

---

## 💭 Developer Process & Technical Decisions

I didn't want to build just another tutorial project. I wanted to create a tool that felt alive, handled real-world
issues, and taught me how to ship code that doesn't break when things get messy. 
I built SoftStack Stockroom to ensure that when a user looks at
this app, it actually works as intended, even when the data isn't clean because I fudged a number during data entry. 

Here are some of the technical decisions I made along the way:

### 1. Robust Type Handling & Defensive UI Rendering

* **The Problem:** In the real world, data is messy. Sometimes a discount comes in as a clean number (20), other times
  as a stubborn string with a percent sign ("20%"). My code would silently fail, hiding the "sale" visuals because
  JavaScript treats "20%" as "Not a Number."
* **The Implementation:** I built a defensive parser that checks the data type first, strips out the % if it's there,
  and forces everything into a clean number before doing any math.

```javascript
const discountVal = typeof item.DiscountPercent === 'string'
    ? parseFloat(item.DiscountPercent.replace('%', ''))
    : parseFloat(item.DiscountPercent || 0);
```

* **Why It Matters:** Normalizing raw inputs before conditional rendering keeps the UI resilient and predictable, regardless of formatting surprises. Now, the UI stays consistent and reliable, no matter how the data gets processed.

---

### 2. Prioritizing Security with Safe DOM Construction

* **The Choice:** While it's tempting to just dump dynamic data into the page using innerHTML, I wanted to avoid any chance of XSS attacks. Even though it is quick to write and looks good on your screen, it's really a shortcut that leaves a door open for attackers. Instead, I opted for a safer approach that constructs DOM elements programmatically. 
* **The Implementation:** I chose to build the table rows the "hard" way—using `document.createElement()` and explicit
  `.textContent` assignment. It takes a few more lines of code, but it’s the secure way and really should be the default for any dynamic content.

```javascript
const origPrice = document.createElement('span');
origPrice.className = 'price-original';
origPrice.textContent = `$${rawPrice.toFixed(2)}`;
priceCell.appendChild(origPrice);
```

* **Why It Matters:** By using `.textContent` the browser automatically treats user input as plain text, not code. If a
  hacker tries to sneak a malicious script into a product name, it just shows up as harmless text instead of executing. It’s about building trust with your users from day one.

---

### 3. Fighting Test Pollution in Pytest

* **The Frustration:** I encountered a problem that is apparently a pretty common pitfall. Test pollution was causing my tests to fail intermittently. I had 21 tests, and sometimes 1 or 2 would fail randomly, even though the code was correct. It was maddening because it made me question whether my code was actually broken or if the tests were just unreliable.
* **The Breakthrough:** I realized my fixture scope was set to `"session"`, meaning the database was setup to only initialize once. This allowed data from earlier tests to persist and interfere with later tests, which was the ghost in my machine. I changed the fixture scope to `"function"` so that the database resets before every single test.

```python
@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """Resets and seeds the database before EVERY single test."""
    reset_database()
```

* **The Result:** After refactoring the setup fixture, this eliminated any and all inter-test dependencies. Now, every test runs in a clean environment, and I can trust the results. It was a small change that made a huge difference in reliability. 

---

### 4. Modernizing the Tech Stack (Pydantic V2 & Security)

* **Pydantic V2:** I didn't want to rely on outdated libraries that might become a security risk or break in the future. I migrated my validation models to Pydantic V2, which is faster and more efficient. This ensures that my data validation is robust and future-proof. It's also more strict and catches errors before they can even cause problems or reach the database. 
* **Auth Flow:** I wanted to make sure that only the correct people could touch the inventory. I implemented a secure login flow using **bcrypt** for password storage and **OAuth2 Bearer Tokens** to verify every single request. Essentially, if you don't have a valid token, you cannot change or delete a single product. This adds a layer of security that is essential for any real-world application. 

---

## ✨ Features You Can See & Feel

* 🎨 **Theme Engine:** Switch on the fly between *Nordic Mist*, *Pastel Cafe*, *Sage & Lavender*, and *Dark Mode*.
* 🏷️ **Smart Pricing Visuals:** Calculates final sale prices instantly and displays struck-through baseline prices for
  discounted items.
* 🔒 **Role Safety:** Login overlay protects backend endpoints, ensuring only authenticated staff can modify or wipe
  inventory.
* 📊 **Clean Pagination & Search:** Search by name or price with dynamic pagination controls to keep the UI snappy.

---

## 📡 API Overview

| Method | Endpoint | What it Does | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/auth/token` | Log in & generate access token | No |
| `GET` | `/products` | Fetch current paginated stock | Yes |
| `GET` | `/products/search` | Search inventory by price or keyword | Yes |
| `POST` | `/products/mod` | Create a new item or edit an existing one | Yes |
| `DELETE` | `/products/bulk-delete` | Remove items safely from stock | Yes |


---


## 🛠️ Run It Locally

1. **Clone the repo:**

```bash
git clone https://github.com/duh-nicole/SoftStack_Stockroom.git
cd SoftStack_Stockroom
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Start the backend:**

```bash
uvicorn main:app --reload
```

4. **Run the test suite:**

```bash
pytest -v
```

5. **Open the frontend:**
   Open `index.html` in your browser!

Thanks for checking out the SoftStack Stockroom! I hope you enjoy exploring the code and the dashboard. If you have any questions or feedback, feel free to reach out or open an issue on GitHub. Happy coding! 
