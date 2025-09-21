import csv
class Account:
    
    def __init__(self, account_type, balance = 0):
        self.account_type = account_type
        self.balance = float(balance)

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