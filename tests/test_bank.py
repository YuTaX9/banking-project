import unittest
import os
import csv
from customer.bank_app import Bank, CheckingAccount, SavingsAccount

class TestBank(unittest.TestCase):

    def setUp(self):
        self.test_file = "bank.csv"
        with open(self.test_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["account_id","first_name","last_name","password","balance_checking",
                             "balance_savings","overdraft_count","is_active","overdraft_limit"])
            writer.writerow(["10001","Alice","Wonder","P@ssword1","1000","5000","0","True","-150"])
            writer.writerow(["10002","Bob","Builder","StrongP@ss2","50","500","0","True","-100"])

        if os.path.exists("transactions.csv"):
            os.remove("transactions.csv")

        self.bank = Bank(file_path=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists("transactions.csv"):
            os.remove("transactions.csv")
        if os.path.exists("10001_statement.txt"):
            os.remove("10001_statement.txt")

    def test_add_new_customer_password_strength(self):
        new_id = self.bank.add_new_customer("Charlie","Chaplin","weakpass")
        self.assertIn(new_id, self.bank.customers)

        new_id2 = self.bank.add_new_customer("Dora","Explorer","Strong1@")
        self.assertIn(new_id2, self.bank.customers)

    def test_deposit_and_withdraw(self):
        self.bank.deposit_mony("10001","checking",500)
        self.assertEqual(self.bank.customers["10001"].checking.balance,1500)
        self.bank.deposit_mony("10001","savings",500)
        self.assertEqual(self.bank.customers["10001"].savings.balance,5500)

        self.bank.withdraw_mony("10001","checking",1000)
        self.assertEqual(self.bank.customers["10001"].checking.balance,500)

        self.bank.withdraw_mony("10002","checking",60)  # 50 - 60 = -10. After fee: -10 - 35 = -45
        acc = self.bank.customers["10002"].checking
        self.assertEqual(acc.balance, -45)
        self.assertEqual(acc.overdraft_count, 1)
        self.assertTrue(acc.is_active)

        with self.assertRaises(ValueError):
            self.bank.withdraw_mony("10002","checking",100) # -45 - 100 = -145. This is below the -100 limit.

    def test_reactivate_account(self):
        self.bank.withdraw_mony("10002","checking",60)
        acc = self.bank.customers["10002"].checking
        self.assertTrue(acc.balance < 0)

        payment = -acc.balance
        reactivated = self.bank.reactivate_account("10002",payment)
        self.assertTrue(reactivated)
        self.assertTrue(acc.is_active)
        self.assertEqual(acc.overdraft_count,0)

    def test_transfer_money(self):
        self.bank.transfer_money("10001","checking","10002","savings",200)
        self.assertEqual(self.bank.customers["10001"].checking.balance,800)
        self.assertEqual(self.bank.customers["10002"].savings.balance,700)

    def test_generate_statement(self):
        self.bank.deposit_mony("10001","checking",100)
        self.bank.withdraw_mony("10001","checking",50)
        self.bank.generate_statement("10001")
        self.assertTrue(os.path.exists("10001_statement.txt"))
        with open("10001_statement.txt") as f:
            content = f.read()
            self.assertIn("Transactions", content)

    def test_top_3_customers_and_bonus(self):
        self.bank.add_new_customer("Eve","Online","Strong3@",500,100)
        self.bank.add_new_customer("Frank","Ocean","Strong4@",700,200)

        initial_balances = {c.account_id: c.checking.balance for c in self.bank.customers.values()}
        
        top3, winner = self.bank.top_3_customers()

        self.assertEqual(len(top3), 3)
        self.assertIn(winner, top3)

        self.assertEqual(winner.checking.balance, initial_balances[winner.account_id] + 100)

if __name__ == "__main__":
    unittest.main()