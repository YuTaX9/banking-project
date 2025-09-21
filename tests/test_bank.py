import unittest
import csv
from customer.bank_app import Bank, CheckingAccount, SavingsAccount

class TestBank(unittest.TestCase):

    def setUp(self):
        self.test_file = 'bank.csv'
        with open(self.test_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['account_id', 'first_name', 'last_name', 'password', 'balance_checking', 'balance_savings', 'overdraft_count', 'is_active'])
            writer.writerow(['10001', 'suresh', 'sigera', 'pass1', '1000', '10000', '0', 'True'])
            writer.writerow(['10002', 'test', 'user', 'pass2', '50', '500', '0', 'True'])
        self.bank = Bank(self.test_file)

    def test_load_customers(self):
        self.assertIn('10001', self.bank.customers)
        self.assertEqual(self.bank.customers['10001']['checking'].balance, 1000.0)
        self.assertEqual(self.bank.customers['10001']['savings'].balance, 10000.0)

