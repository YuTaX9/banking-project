# Bank Management System

A simple banking system built with Python. It allows customers to:

* Create new accounts with strong password validation.
* Deposit and withdraw money (with overdraft protection for only checking accounts).
* Transfer money between accounts.
* Generate account statements.
* Log all transactions into a CSV file.

This project demonstrates the use of **Object-Oriented Programming**, **file handling (CSV)**, and **unit testing** in Python.

---

## Example Code

One of the features I’m proud of is the **overdraft protection system** for checking accounts. It applies a fee when going into overdraft and deactivates the account if the limit is exceeded multiple times.

```python
class CheckingAccount(Account):
    OVERDRAFT_FEE = 35  

    def withdraw(self, amount):
        if not self.is_active:
            raise ValueError("Account is deactivated due to multiple overdrafts.")

        projected_balance = self.balance - amount
        fee = 0

        if projected_balance < 0:
            if (projected_balance - self.OVERDRAFT_FEE) < self.overdraft_limit:
                raise ValueError("Withdrawal would exceed overdraft limit.")

            self.balance = projected_balance - self.OVERDRAFT_FEE
            fee = self.OVERDRAFT_FEE
            self.overdraft_count += 1

            if self.overdraft_count >= 2:
                self.is_active = False
        else:
            self.balance = projected_balance

        return self.balance, fee
```

---

## What I Learned

* How to design and structure a project using **OOP principles**.
* How to handle **file persistence** with CSV to store data.
* How to write **unit tests** to ensure correctness of each feature.
* How to design systems that mimic **real-world rules** (e.g., overdraft fees, account deactivation).

---

## Tech Stack

* **Python 3**
* **unittest** for testing
* **CSV files** for data storage

---

## Next Steps

* Add a command-line interface for easier interaction.
* Explore integrating with a database instead of CSV.
* Add encryption for password storage.