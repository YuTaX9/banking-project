import unittest
import os
import csv
from customer.bank_app import Bank
class TestBankFull(unittest.TestCase):

    def setUp(self):
        self.test_file = "bank.csv"
        with open(self.test_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["account_id","first_name","last_name","password","balance_checking","balance_savings"])
            writer.writerow(["10001","Alice","Wonder","P@ssword1","1000","5000"])
            writer.writerow(["10002","Bob","Builder","StrongP@ss2","50","500"])
        if os.path.exists("transactions.csv"):
            os.remove("transactions.csv")
        self.bank = Bank(self.test_file)

    def tearDown(self):
        for f in [self.test_file, "transactions.csv", "10001_statement.txt", "10002_statement.txt"]:
            if os.path.exists(f):
                os.remove(f)

    def test_deposit_checking_and_savings(self):
        self.bank.deposit_money("10001","checking",500)
        self.bank.deposit_money("10001","savings",500)
        self.assertEqual(self.bank.customers["10001"].checking.balance,1500)
        self.assertEqual(self.bank.customers["10001"].savings.balance,5500)

    def test_deposit_negative_raises(self):
        with self.assertRaises(ValueError):
            self.bank.deposit_money("10001","checking",-50)

    def test_withdraw_within_balance(self):
        self.bank.withdraw_money("10001","checking",500)
        self.assertEqual(self.bank.customers["10001"].checking.balance,500)

    def test_withdraw_causing_overdraft_within_limit(self):
        new_balance, fee = self.bank.withdraw_money("10002","checking",60)
        self.assertEqual(new_balance,-45)
        self.assertEqual(self.bank.customers["10002"].checking.overdraft_count,1)
        self.assertTrue(self.bank.customers["10002"].checking.is_active)

    def test_withdraw_exceeding_overdraft_limit(self):
        with self.assertRaises(ValueError):
            self.bank.withdraw_money("10002","checking",200)

    def test_transfer_between_accounts(self):
        self.bank.transfer_money("10001","checking","10002","savings",200)
        self.assertEqual(self.bank.customers["10001"].checking.balance,800)
        self.assertEqual(self.bank.customers["10002"].savings.balance,700)

    def test_transfer_exceeding_balance_raises(self):
        with self.assertRaises(ValueError):
            self.bank.transfer_money("10002","checking","10001","savings",200)

    def test_reactivate_account_fails_with_negative_balance(self):
        self.bank.withdraw_money("10002","checking",60)
        with self.assertRaises(ValueError):
            self.bank.reactivate_account("10002","checking")

    def test_reactivate_account_success(self):
        acc = self.bank.customers["10001"].checking


        acc.is_active = False
        acc.balance = 0

        result = self.bank.reactivate_account("10001", "checking")

        self.assertTrue(result)
        self.assertTrue(acc.is_active)
        self.assertEqual(acc.overdraft_count, 0)


    def test_generate_statement_creates_file(self):
        self.bank.deposit_money("10001","checking",100)
        self.bank.withdraw_money("10001","checking",50)
        self.bank.generate_statement("10001")
        self.assertTrue(os.path.exists("10001_statement.txt"))
        with open("10001_statement.txt") as f:
            content = f.read()
            self.assertIn("Transactions", content)

    def test_add_new_customer_strong_and_weak_password(self):
        with self.assertRaises(ValueError):
            self.bank.add_new_customer("Charlie","Chaplin","weakpass")
        new_id = self.bank.add_new_customer("Dora","Explorer","Strong1@")
        self.assertIn(new_id,self.bank.customers)

    def test_top_3_customers_ranking(self):
        self.bank.add_new_customer("Eve","Online","Strong2@",500,100)
        self.bank.add_new_customer("Frank","Ocean","Strong3@",700,200)
        top3 = self.bank.top_3_customers()
        self.assertEqual(len(top3),3)
        balances = [c.checking.balance+c.savings.balance for c in top3]
        self.assertTrue(balances[0]>=balances[1]>=balances[2])

if __name__=="__main__":
    unittest.main()
