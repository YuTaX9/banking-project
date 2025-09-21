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
                    print('file are readd')
        except FileNotFoundError:
            print(f"Warning: {self.file_path} not found. Starting with an empty database.")

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

if __name__ == "__main__":
    Bank()


