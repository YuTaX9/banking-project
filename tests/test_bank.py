import unittest
import csv
import os
from customer.bank_app import Bank, CheckingAccount, SavingsAccount

class TestBank(unittest.TestCase):

    def setUp(self):
        self.test_file = 'bank.csv'
        with open(self.test_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['account_id', 'first_name', 'last_name', 'password', 'balance_checking', 'balance_savings', 'overdraft_count', 'is_active'])
            writer.writerow(['10001', 'suresh', 'sigera', 'pass1', '1000', '10000', '0', 'True'])
            writer.writerow(['10002', 'test', 'user', 'pass2', '50', '500', '0', 'True'])
        if os.path.exists('transactions.csv'):
            os.rename('transactions.csv')
        self.bank = Bank(self.test_file)
    
    # def tearDown(self):
    #     if os.path.exists(self.test_file):
    #         os.remove(self.test_file)
    #     if os.path.exists('transactions.csv'):
    #         os.remove('transactions.csv')


    def test_load_customers(self):
        self.assertIn('10001', self.bank.customers)
        self.assertEqual(self.bank.customers['10001']['checking'].balance, 1000.0)
        self.assertEqual(self.bank.customers['10001']['savings'].balance, 10000.0)

    def test_add_new_customer(self):
        new_id = self.bank.add_new_customer("Bassam", "Alghamdi", "password")
        self.assertIn(new_id, self.bank.customers)
        self.assertEqual(self.bank.customers[new_id]['first_name'], "Bassam")

    def test_deposit(self):
        self.bank.deposit_mony('10001', 'checking', 500)
        self.assertEqual(self.bank.customers['10001']['checking'].balance, 1500.0)

    def test_withdraw_success(self):
        self.bank.withdraw_mony('10001', 'checking', 200)
        self.assertEqual(self.bank.customers['10001']['checking'].balance, 800.0)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.bank.withdraw_mony('10001', 'checking', 1500)

    def test_overdraft_first_time(self):
        self.bank.withdraw_mony('10002', 'checking', 100)
        customer_account = self.bank.customers['10002']['checking']
        self.assertEqual(customer_account.balance, 50 - 100 - CheckingAccount.OVERDRAFT_FEE)
        self.assertEqual(customer_account.overdraft_count, 1)
        self.assertTrue(customer_account.is_active)

    def test_overdraft_deactivation(self):
        self.bank.withdraw_mony('10002', 'checking', 100)
        self.bank.withdraw_mony('10002', 'checking', 10)
        customer_account = self.bank.customers['10002']['checking']
        self.assertEqual(customer_account.overdraft_count, 2)
        self.assertFalse(customer_account.is_active)

    def test_reactivate_account_with_payment(self):
        self.bank.withdraw_mony('10002', 'checking', 60)
        self.bank.withdraw_mony('10002', 'checking', 10)
        customer_account = self.bank.customers['10002']['checking']
        self.assertFalse(customer_account.is_active)

        payment_needed = -customer_account.balance
        reactivated = self.bank.reactivate_account('10002', payment_needed)
        self.assertTrue(reactivated)
        self.assertTrue(customer_account.is_active)
        self.assertEqual(customer_account.overdraft_count, 0)

    def test_transfer_money(self):
        self.bank.transfer_money('10001', 'checking', '10002', 'checking', 100)
        self.assertEqual(self.bank.customers['10001']['checking'].balance, 900.0)
        self.assertEqual(self.bank.customers['10002']['checking'].balance, 150.0)

if __name__ == '__main':
    unittest.main()