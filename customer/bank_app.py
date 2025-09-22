import csv
class Account:
    
    def __init__(self, account_type, balance = 0):
        self.account_type = account_type
        self.balance = float(balance)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError('Deposit amount must be positive.')
        self.balance += amount
        return self.balance
    
    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError('Withdrawal amount must be positive.')
        if self.balance < amount:
            raise ValueError('Insufficient funds.')
        self.balance -= amount
        return self.balance

class CheckingAccount(Account):
    
    def __init__(self, balance = 0, overdraft_count = 0, is_active = True):
        super().__init__('checking', balance)
        self.overdraft_count = int(overdraft_count)

        if isinstance(is_active, bool):
            self.is_active = is_active
        else:
            (is_active.lower() == 'true')
        



class SavingsAccount(Account):
    
    def __init__(self, balance = 0):
        super().__init__("savings", balance)

class Bank:
    def __init__(self, file_path = 'bank.csv'):
        self.file_path = file_path
        self.customers = {}
        self.load_customers()

    def load_customers(self):
        try:
            with open(self.file_path, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    account_id = row['account_id']

                    overdraft_count = int(row.get('overdraft_count', 0))
                    is_active = row.get('is_active', 'True').lower() == 'true'

                    self.customers[account_id] = {
                        'first_name': row['first_name'],
                        "last_name": row['last_name'],
                        "password": row['password'],
                        "checking": CheckingAccount(row['balance_checking'], overdraft_count, is_active),
                        "savings": SavingsAccount(row['balance_savings'])
                    }
        except FileNotFoundError:
            print(f"Warning: {self.file_path} not found. Starting with an empty database.")

    def save_customer(self):
        fieldnames = ['account_id', 'first_name', 'last_name', 'password', 'balance_checking', 'balance_savings', 'overdraft_count', 'is_active']
        with open(self.file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames = fieldnames)
            writer.writeheader()
            for account_id, info in self.customers.items():
                writer.writerow({
                    'account_id': account_id,
                    'first_name': info['first_name'],
                    'last_name': info['last_name'],
                    'password': info['password'],
                    'balance_checking': info['checking'].balance,
                    'balance_savings': info['savings'].balance,
                    'overdraft_count': info['checking'].overdraft_count,
                    'is_active': info['checking'].is_active
                })

    def add_new_customer(self, first_name, last_name, password, initial_checking = 0, initial_savings = 0):
        new_account_id = str(len(self.customers) + 10001)
        self.customers[new_account_id] = {
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
            "checking": CheckingAccount(initial_checking),
            "savings": SavingsAccount(initial_savings)
        }
        self.save_customer()
        print('customer are saved')
        return new_account_id


    def deposit_mony(self, account_id, account_type, amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError('Customer not found')
        
        if account_type == 'checking':
            customer['checking'].deposit(amount)
        elif account_type == 'savings':
            customer['savings'].deposit(amount)
        else:
            raise ValueError('Invalid account type.')
    
    def withdraw_mony(self, account_id, account_type, amount):
        customer = self.customers.get(account_id)
        if not customer:
            raise ValueError('Customer not found.')
        
        if account_type == 'checking':
            customer['checking'].withdraw(amount)
        elif account_type == 'savings':
            customer['savings'].withdraw(amount)
        else:
            raise ValueError('Invalid account type.')

if __name__ == "__main__":
    bank = Bank()

    if '10001' in bank.customers:
        try:
            bank.deposit_mony('10001', 'checking', 100)
            print("Deposit successful.")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Customer with ID '10001' not found. Cannot deposit money.")

    if '10002' in bank.customers:
        try:
            bank.withdraw_mony('10002', 'savings', 100)
            print("withdraw successful.")
        except ValueError as e:
            print(f"Error: {e}")
    else:
        print("Customer with ID '10002' not found. Cannot withdraw money.")

    try:
        print("Attempting to add a new customer...")
        new_account_id = bank.add_new_customer("Bassam", "Alghamdi", "aabbpass123", 500, 1000)
        print(f"New customer added with ID: {new_account_id}")
        print('-----------------------------------------')
    except Exception as e:
        print(f"Failed to add a new customer. Error: {e}")



