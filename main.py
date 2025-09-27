from customer.bank_app import Bank
from colorama import Fore, init

init(autoreset=True)

def print_banner():
    print(Fore.CYAN + "=" * 40)
    print(Fore.YELLOW + "     ✨ Welcome to ACME Bank ✨")
    print(Fore.CYAN + "=" * 40 + "\n")

def success(msg):
    print(Fore.GREEN + "✅ " + msg)

def error(msg):
    print(Fore.RED + "❌ " + msg)

def info(msg):
    print(Fore.BLUE + "ℹ️ " + msg)

def show_dashboard(customer):
    print("\n" + Fore.MAGENTA + "=" * 30)
    print(Fore.CYAN + f" Welcome {customer.first_name} {customer.last_name}!")
    print(Fore.YELLOW + f" 💳 Checking: {customer.checking.balance} {customer.checking.currency}")
    print(Fore.YELLOW + f" 💰 Savings : {customer.savings.balance} {customer.savings.currency}")
    total = customer.checking.balance + customer.savings.balance
    print(Fore.GREEN + f" ------------------------------")
    print(Fore.GREEN + f" Total Balance: {total} {customer.checking.currency}")
    print(Fore.MAGENTA + "=" * 30 + "\n")

def main():
    bank = Bank()
    print_banner()

    while True:
        print(Fore.CYAN + "Main Menu:")
        print("1. Add New Customer")
        print("2. Login")
        print("3. Show Top 3 Customers")
        print("q. Quit")

        choice = input(Fore.YELLOW + "Choose an option: ").strip().lower()
        if choice == "1":
            first = input("First name: ")
            last = input("Last name: ")
            while True:
                pwd = input(Fore.YELLOW + "Password: ")
                try:
                    new_id = bank.add_new_customer(first, last, pwd)
                    success(f"New customer added with ID: {new_id}")
                    break
                except Exception as e:
                    error(str(e))
                    print(Fore.RED + "Please try again with a stronger password.\n")

        elif choice == "2":
            account_id = input("Account ID: ")
            pwd = input("Password: ")
            if bank.log_in(account_id, pwd):
                customer = bank.customers[account_id]
                success("Login successful!")
                show_dashboard(customer)

                while True:
                    print(Fore.CYAN + "\n--- Account Menu ---")
                    print("1. Deposit")
                    print("2. Withdraw")
                    print("3. Transfer")
                    print("4. Show Balances")
                    print("5. Generate Statement")
                    print("6. Reactivate Checking Account")
                    print("b. Back to Main Menu")
                    print("q. Quit")

                    acc_choice = input(Fore.YELLOW + "Choose an option: ").strip().lower()
                    try:
                        if acc_choice == "1":
                            acc_type = input("Account (checking/savings): ").lower()
                            amount = float(input("Amount: "))
                            bank.deposit_money(account_id, acc_type, amount)
                            success(f"Deposited {amount} into {acc_type}")

                        elif acc_choice == "2":
                            acc_type = input("Account (checking/savings): ").lower()
                            amount = float(input("Amount: "))
                            new_balance, fee = bank.withdraw_money(account_id, acc_type, amount)
                            success(f"Withdrew {amount} from {acc_type}. New balance: {new_balance}, Fee: {fee}")

                        elif acc_choice == "3":
                            target_id = input("Target Account ID: ")
                            from_acc = input("From (checking/savings): ").lower()
                            to_acc = input("To (checking/savings): ").lower()
                            amount = float(input("Amount: "))
                            bank.transfer_money(account_id, from_acc, target_id, to_acc, amount)
                            success(f"Transferred {amount} from {from_acc} to {to_acc} ({target_id})")

                        elif acc_choice == "4":
                            show_dashboard(customer)

                        elif acc_choice == "5":
                            bank.generate_statement(account_id)
                            success("Statement generated successfully!")

                        elif acc_choice == "6":
                            try:
                                bank.reactivate_account(account_id, "checking")
                                success("Checking account reactivated successfully!")
                            except Exception as e:
                                error(str(e))

                        elif acc_choice == "b":
                            info("Returning to Main Menu...")
                            break

                        elif acc_choice == "q":
                            info("Goodbye 👋")
                            return

                        else:
                            error("Invalid choice. Try again.")
                    except Exception as e:
                        error(str(e))

            else:
                error("Login failed. Check your Account ID or Password.")

        elif choice == "3":
            try:
                top_customers = bank.top_3_customers()
                print(Fore.CYAN + "\n--- Top 3 Customers ---")
                for idx, cust in enumerate(top_customers, 1):
                    total = cust.checking.balance + cust.savings.balance
                    print(f"{idx}. {cust.first_name} {cust.last_name} (Total: {total})")
            except Exception as e:
                error(str(e))

        elif choice == "q":
            info("Goodbye 👋")
            break
        else:
            error("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
