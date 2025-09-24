import csv
import os
from datetime import datetime

# Account Classes
class Account:
    def __init__(self, account_type, balance=0):
        self.account_type = account_type
        self.balance = float(balance)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        return self.balance

class CheckingAccount(Account):
    OVERDRAFT_FEE = 35
    OVERDRAFT_LIMIT = -100

    def __init__(self, balance=0, overdraft_count=0, is_active=True):
        super().__init__("checking", balance)
        self.overdraft_count = int(overdraft_count)
        self.is_active = bool(is_active) if isinstance(is_active, bool) else str(is_active).lower() == "true"
    
    def withdraw(self, amount):
        if not self.is_active:
            raise ValueError("Account is deactivated due to multiple overdrafts.")
    
        if amount <= 0:
            raise ValueError("Withdrawal must be positive.")

        projected_balance = self.balance - amount
        

        if projected_balance < 0:

            self.balance = projected_balance - self.OVERDRAFT_FEE
            self.overdraft_count += 1

            if self.balance < self.OVERDRAFT_LIMIT:
                raise ValueError("Withdrawal would exceed overdraft limit.")
            
            if self.overdraft_count >= 2:
                self.is_active = False
            
            return self.balance, self.OVERDRAFT_FEE
        else:
            self.balance = projected_balance
            return self.balance, 0

    def reactivate(self):
        self.is_active = True
        self.overdraft_count = 0

    def pay(self, amount):
        if amount <= 0:
            raise ValueError("Payment must be positive.")
        self.balance += amount
        return self.balance

class SavingsAccount(Account):
    def __init__(self, balance=0):
        super().__init__("savings", balance)

# Customer Class
class Customer:
    def __init__(self, account_id, first_name, last_name, password,
                 checking_balance=0, savings_balance=0, overdraft_count=0, is_active=True):
        self.account_id = account_id
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.checking = CheckingAccount(checking_balance, overdraft_count, is_active)
        self.savings = SavingsAccount(savings_balance)

    @property
    def is_active(self):
        return self.checking.is_active

    @property
    def overdraft_count(self):
        return self.checking.overdraft_count

# Transaction Logger
class TransactionLogger:
    FILE = "transactions.csv"
    FIELDNAMES = ["tx_id", "timestamp", "type", "from_account_id", "from_account_type",
                  "to_account_id", "to_account_type", "amount", "fee", "resulting_balance"]

    def __init__(self, file_path=None):
        self.file_path = file_path or self.FILE
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode="w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()

    def _next_tx_id(self):
        try:
            with open(self.file_path, mode="r", newline="") as f:
                reader = csv.DictReader(f)
                max_id = 0
                for row in reader:
                    try:
                        tid = int(row.get("tx_id", 0))
                        max_id = max(max_id, tid)
                    except (ValueError, TypeError):
                        continue
                return max_id + 1
        except FileNotFoundError:
            return 1

    def log(self, tx_type, from_id, from_type, to_id, to_type, amount, fee, resulting_balance):
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
        with open(self.file_path, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writerow(tx)

# Bank Class
class Bank:
    def __init__(self, file_path="bank.csv", tx_logger=None):
        self.file_path = file_path
        self.customers = {}
        self.tx_logger = tx_logger or TransactionLogger()
        self.load_customers()

    def load_customers(self):
        try:
            with open(self.file_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    account_id = row["account_id"]
                    is_active_val = row.get("is_active", "True").lower() == "true"
                    cust = Customer(
                        account_id,
                        row.get("first_name") or "",
                        row.get("last_name") or "",
                        row.get("password") or "",
                        float(row.get("balance_checking", 0)),
                        float(row.get("balance_savings", 0)),
                        int(row.get("overdraft_count", 0)),
                        is_active_val,
                    )
                    self.customers[account_id] = cust
        except FileNotFoundError:
            print(f"Warning: {self.file_path} not found. Starting with empty database.")
        except Exception as e:
            print(f"Error loading customers: {e}")

    def save_customers(self):
        fieldnames = ["account_id", "first_name", "last_name", "password",
                      "balance_checking", "balance_savings", "overdraft_count", "is_active"]
        with open(self.file_path, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for cust in self.customers.values():
                writer.writerow({
                    "account_id": cust.account_id,
                    "first_name": cust.first_name,
                    "last_name": cust.last_name,
                    "password": cust.password,
                    "balance_checking": cust.checking.balance,
                    "balance_savings": cust.savings.balance,
                    "overdraft_count": cust.overdraft_count,
                    "is_active": str(cust.is_active),
                })

    def add_new_customer(self, first_name, last_name, password, initial_checking=0, initial_savings=0):
        if self.customers:
            max_id = max(int(k) for k in self.customers.keys())
            new_account_id = str(max_id + 1)
        else:
            new_account_id = "10001"

        cust = Customer(new_account_id, first_name, last_name, password, initial_checking, initial_savings)
        self.customers[new_account_id] = cust
        self.save_customers()
        return new_account_id

    def log_in(self, account_id, password):
        return account_id in self.customers and self.customers[account_id].password == password

    def deposit_mony(self, account_id, account_type, amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found")

        fee = 0
        if account_type == "checking":
            new_balance = customer.checking.deposit(amount)
            resulting_balance = new_balance
        elif account_type == "savings":
            new_balance = customer.savings.deposit(amount)
            resulting_balance = new_balance
        else:
            raise ValueError("Invalid account type.")

        self.tx_logger.log("deposit", None, None, account_id, account_type, amount, fee, resulting_balance)
        self.save_customers()

    def withdraw_mony(self, account_id, account_type, amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found.")

        fee = 0
        if account_type == "checking":
            new_balance, fee = customer.checking.withdraw(amount)
            resulting_balance = new_balance
        elif account_type == "savings":
            new_balance = customer.savings.withdraw(amount)
            resulting_balance = new_balance
        else:
            raise ValueError("Invalid account type.")

        self.tx_logger.log("withdraw", account_id, account_type, None, None, amount, fee, resulting_balance)
        self.save_customers()

    def transfer_money(self, from_id, from_type, to_id, to_type, amount):
        from_cust = self.customers.get(from_id)
        to_cust = self.customers.get(to_id)
        if not from_cust or not to_cust:
            raise ValueError("One or both customers not found.")

        if from_type == "checking":
            new_balance_from, fee = from_cust.checking.withdraw(amount)
        elif from_type == "savings":
            new_balance_from = from_cust.savings.withdraw(amount)
            fee = 0
        else:
            raise ValueError("Invalid source account type.")

        if to_type == "checking":
            to_cust.checking.deposit(amount)
        elif to_type == "savings":
            to_cust.savings.deposit(amount)
        else:
            raise ValueError("Invalid destination account type.")

        self.tx_logger.log("transfer", from_id, from_type, to_id, to_type, amount, fee, new_balance_from)
        self.save_customers()

    def reactivate_account(self, account_id, payment_amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError("Customer not found.")

        if payment_amount <= 0:
            raise ValueError("Payment amount must be positive.")

        customer.checking.pay(payment_amount)
        self.tx_logger.log("payment", None, None, account_id, "checking", payment_amount, 0, customer.checking.balance)

        reactivated = False
        if customer.checking.balance >= 0:
            customer.checking.reactivate()
            reactivated = True
            self.tx_logger.log("reactivation", None, None, account_id, "checking", 0, 0, customer.checking.balance)

        self.save_customers()
        return reactivated