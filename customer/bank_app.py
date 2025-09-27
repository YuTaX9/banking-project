import csv
import os
import re
from datetime import datetime

class Account:
    def __init__(self, account_type, balance = 0, currency="SAR"):
        self.account_type = account_type
        self.balance = float(balance)
        self.currency = currency

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        return self.balance # Return new balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        return self.balance

class CheckingAccount(Account):
    OVERDRAFT_FEE = 35 # Fee if overdraft happens

    def __init__(self, balance = 0, overdraft_limit = -100):
        super().__init__("checking", balance)
        self.overdraft_limit = overdraft_limit
        self.overdraft_count = 0
        self.is_active = True

    def withdraw(self, amount):
        if not self.is_active:
            raise ValueError("Account is deactivated due to multiple overdrafts.")

        if amount <= 0:
            raise ValueError("Withdrawal must be positive.")

        projected_balance = self.balance - amount
        fee = 0

        if projected_balance < 0: # Overdraft
            if (projected_balance - self.OVERDRAFT_FEE) < self.overdraft_limit:
                raise ValueError("Withdrawal would exceed overdraft limit.")

            self.balance = projected_balance - self.OVERDRAFT_FEE
            fee = self.OVERDRAFT_FEE
            self.overdraft_count += 1

            if self.overdraft_count >= 2: # 2 overdrafts → deactivate
                self.is_active = False
        else:
            self.balance = projected_balance

        return self.balance, fee

class SavingsAccount(Account):
    def __init__(self, balance=0):
        super().__init__("savings", balance)

    def withdraw(self, amount):
        new_balance = super().withdraw(amount)
        return new_balance, 0

class Customer:
    def __init__(self, account_id, first_name, last_name, password,
                 balance_checking=0, balance_savings=0):
        self.account_id = account_id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.checking = CheckingAccount(balance_checking)
        self.savings = SavingsAccount(balance_savings)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class TransactionLogger:
    FIELDNAMES = ["tx_id", "timestamp", "type", "from_account_id", "from_account_type",
                  "to_account_id", "to_account_type", "amount", "fee", "resulting_balance"]

    def __init__(self, filename="transactions.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def _next_tx_id(self): # Generate next transaction ID
        max_id = 0
        if os.path.exists(self.filename):
            with open(self.filename, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        max_id = max(max_id, int(row.get("tx_id", 0)))
                    except:
                        continue
        return max_id + 1

    def log(self, tx_type, from_id=None, from_type=None, to_id=None, to_type=None, amount=0, fee=0, resulting_balance=0):
        tx = {
            "tx_id": self._next_tx_id(),
            "timestamp": datetime.now().isoformat(),
            "type": tx_type,
            "from_account_id": from_id or "",
            "from_account_type": from_type or "",
            "to_account_id": to_id or "",
            "to_account_type": to_type or "",
            "amount": amount,
            "fee": fee,
            "resulting_balance": resulting_balance,
        }
        with open(self.filename, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerow(tx)

    def get_transactions_for_customer(self, account_id):
        tx_list = []
        if not os.path.exists(self.filename):
            return tx_list
        with open(self.filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("from_account_id") == account_id or row.get("to_account_id") == account_id:
                    tx_list.append(row)
        return tx_list

class Bank:
    def __init__(self, filename="bank.csv"):
        self.filename = filename
        self.customers = {}
        self.tx_logger = TransactionLogger()
        self.load_customers()

    def load_customers(self):
        if not os.path.exists(self.filename):
            return
        with open(self.filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.customers[row["account_id"]] = Customer(
                    row["account_id"], row["first_name"], row["last_name"],
                    row["password"], float(row["balance_checking"]), float(row["balance_savings"])
                )

    def save_customers(self):
        with open(self.filename, "w", newline="") as f:
            fieldnames = ["account_id", "first_name", "last_name", "password",
                          "balance_checking", "balance_savings"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for cust in self.customers.values():
                writer.writerow({
                    "account_id": cust.account_id,
                    "first_name": cust.first_name,
                    "last_name": cust.last_name,
                    "password": cust.password,
                    "balance_checking": cust.checking.balance,
                    "balance_savings": cust.savings.balance
                })

    @staticmethod
    def is_strong_password(password):
        return (
            len(password) >= 8
            and re.search(r"[A-Za-z]", password)
            and re.search(r"[0-9]", password)
            and re.search(r"[@$!%*?&]", password)
        )

    def add_new_customer(self, first_name, last_name, password, initial_checking=0, initial_savings=0):
        if self.customers:
            max_id = max(int(k) for k in self.customers.keys())
            new_account_id = str(max_id + 1)
        else:
            new_account_id = "10001"

        if not self.is_strong_password(password):
            raise ValueError("Password too weak! Must be at least 8 chars with letters, numbers, and symbols.")

        self.customers[new_account_id] = Customer(
            new_account_id, first_name, last_name, password,
            initial_checking, initial_savings
        )
        self.save_customers()
        return new_account_id

    def log_in(self, account_id, password):
        customer = self.customers.get(account_id)
        if not customer:
            return False
        return customer.password == password

    def deposit_money(self, account_id, account_type, amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found.")

        if account_type == "checking":
            new_balance = customer.checking.deposit(amount)
        elif account_type == "savings":
            new_balance = customer.savings.deposit(amount)
        else:
            raise ValueError("Invalid account type.")

        self.tx_logger.log(
            tx_type="deposit",
            to_id=account_id,
            to_type=account_type,
            amount=amount,
            resulting_balance=new_balance
        )
        self.save_customers()
        return new_balance

    def withdraw_money(self, account_id, account_type, amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found.")

        if account_type == "checking":
            new_balance, fee = customer.checking.withdraw(amount)
        elif account_type == "savings":
            new_balance, fee = customer.savings.withdraw(amount)
        else:
            raise ValueError("Invalid account type.")

        self.tx_logger.log(
            tx_type="withdraw",
            from_id=account_id,
            from_type=account_type,
            amount=amount,
            fee=fee,
            resulting_balance=new_balance
        )
        self.save_customers()
        return new_balance, fee

    def transfer_money(self, from_id, from_type, to_id, to_type, amount):
        sender = self.customers.get(from_id)
        receiver = self.customers.get(to_id)
        if not sender or not receiver:
            raise ValueError("Sender or receiver not found.")

        if from_type == "checking":
            sender_new, fee = sender.checking.withdraw(amount)
        elif from_type == "savings":
            sender_new, fee = sender.savings.withdraw(amount)
        else:
            raise ValueError("Invalid sender account type.")

        if to_type == "checking":
            receiver_new = receiver.checking.deposit(amount)
        elif to_type == "savings":
            receiver_new = receiver.savings.deposit(amount)
        else:
            raise ValueError("Invalid receiver account type.")

        self.tx_logger.log(
            tx_type="transfer",
            from_id=from_id,
            from_type=from_type,
            to_id=to_id,
            to_type=to_type,
            amount=amount,
            fee=fee,
            resulting_balance=sender_new
        )
        self.save_customers()
        return sender_new, receiver_new

    def reactivate_account(self, account_id, account_type):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found.")

        if account_type != "checking":
            raise ValueError("Only checking accounts can be reactivated.")

        if customer.checking.is_active:
            raise ValueError("Account already active.")

        if customer.checking.balance < 0:
            raise ValueError(f"Cannot reactivate account. Outstanding overdraft: {customer.checking.balance}")

        customer.checking.is_active = True
        customer.checking.overdraft_count = 0

        self.tx_logger.log(
        "reactivate",
        account_id,
        account_type,
        None,
        None,
        0,
        0,
        customer.checking.balance
        )


        self.save_customers()
        return True


    def generate_statement(self, account_id):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found.")

        tx_list = self.tx_logger.get_transactions_for_customer(account_id)
        with open(f"{account_id}_statement.txt", "w") as f:
            f.write(f"Customer: {customer.first_name} {customer.last_name}\n")
            f.write(f"Checking Balance: {customer.checking.balance}\n")
            f.write(f"Savings Balance: {customer.savings.balance}\n")
            f.write(f"Overdrafts: {customer.checking.overdraft_count}\n")
            f.write("Transactions:\n")
            for tx in tx_list:
                f.write(
                    f"{tx['timestamp']} | {tx['type']} | Amount: {tx['amount']} | Fee: {tx['fee']} | Balance: {tx['resulting_balance']}\n"
                )

    def top_3_customers(self):
        ranked = sorted(
            self.customers.values(),
            key=lambda c: c.checking.balance + c.savings.balance,
            reverse=True
        )
        return ranked[:3]