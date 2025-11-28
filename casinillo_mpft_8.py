import datetime
import json
import os
from typing import List, Optional

class FinancialRecord:
    def __init__(self, date: datetime.date, description: str, amount: float, 
                 due_date: Optional[str] = None, record_type: str = "expense"):
        self.date = date
        self.description = description
        self.amount = amount
        self.due_date = due_date
        self.record_type = record_type  # "expense" or "income"

    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'description': self.description,
            'amount': self.amount,
            'due_date': self.due_date,
            'record_type': self.record_type
        }

    @classmethod
    def from_dict(cls, data):
        date = datetime.date.fromisoformat(data['date'])
        return cls(date, data['description'], data['amount'], 
                  data.get('due_date'), data.get('record_type', 'expense'))

    def __str__(self):
        sign = "+" if self.record_type == "income" else "-"
        due_date_info = f" | Due: {self.due_date}" if self.due_date else ""
        return f"{self.date} | {self.description} | {sign}₱{abs(self.amount):.2f}{due_date_info}"

class FinanceTracker:
    def __init__(self, data_file="financial_data.json"):
        self.plans: List[FinancialRecord] = []
        self.trash_bin: List[FinancialRecord] = []
        self.data_file = data_file
        self.load_data()

    def add_record(self, record: FinancialRecord):
        self.plans.append(record)
        self.save_data()

    def add_plan_interactive(self):
        print("\nAdd New Financial Record")

        while True:
            record_type = input("Enter record type ('plan' or 'allowance'): ").strip().lower()
            if record_type in ("plan", "allowance"):
                # Map 'plan' to 'expense' and 'allowance' to 'income' for internal use
                record_type = "expense" if record_type == "plan" else "income"
                break
            else:
                print("Invalid record type. Please enter 'plan' or 'saving'.")

        # Date input with validation
        while True:
            date_str = input("Enter date (MM-DD-YYYY): ").strip()
            try:
                date = datetime.datetime.strptime(date_str, '%m-%d-%Y').date()
                break
            except ValueError:
                print("Invalid date format. Please use MM-DD-YYYY.")

        description = input("Enter description: ").strip()
        if not description:
            print("Description cannot be empty.")
            return

        # Amount input with validation
        while True:
            try:
                amount = float(input("Enter amount: "))
                if amount <= 0:
                    print("Invalid Amount.")
                    continue
                break
            except ValueError:
                print("Invalid amount. Please enter a number.")

        due_date = None
        if record_type == "expense":
            due_date = input("Enter due date (optional, press Enter to skip): ").strip()
            if not due_date:
                due_date = None

        record = FinancialRecord(date, description, amount, due_date, record_type)
        self.add_record(record)
        print(f"{'Plan' if record_type == 'expense' else 'Allowance'} record added successfully!")

    def view_plans(self, plans_list: Optional[List[FinancialRecord]] = None):
        plans_to_view = plans_list if plans_list is not None else self.plans
        
        if not plans_to_view:
            print("No records to display.")
            return

        print(f"\n{'#':<3} {'Date':<12} {'Description':<20} {'Amount':<10} {'Due Date':<15} {'Type':<8}")
        print("-" * 75)
        for i, plan in enumerate(plans_to_view):
            amount_str = f"+₱{plan.amount:.2f}" if plan.record_type == "income" else f"-₱{plan.amount:.2f}"
            due_date = plan.due_date if plan.due_date else "N/A"
            record_type_display = "Allowance" if plan.record_type == "income" else "Plan"  # Display "Allowance" or "Plan"
            print(f"{i+1:<3} {plan.date:<12} {plan.description:<20} {amount_str:<10} {due_date:<15} {record_type_display:<8}")

    def calculate_balance(self) -> dict:
        print("\n--- Allowance and Plans Details ---")
        for plan in self.plans:
            sign = "+" if plan.record_type == "income" else "-"
            record_type_display = "Allowance" if plan.record_type == "income" else "Plan"  # Display "Allowance" or "Plan"
            print(f"{plan.description} ({record_type_display}): {sign}₱{abs(plan.amount):.2f}")

        total_income = sum(plan.amount for plan in self.plans if plan.record_type == "income")
        total_expenses = sum(plan.amount for plan in self.plans if plan.record_type == "expense")
        net_balance = total_income - total_expenses
        
        return {
            'income': total_income,
            'expenses': total_expenses,
            'net_balance': net_balance
        }

    def display_balance_report(self):
        balance = self.calculate_balance()
        print("\n--- Financial Balance Report ---")
        print(f"Total Allowances:    ₱{balance['income']:.2f}")
        print(f"Total Plans:  ₱{balance['expenses']:.2f}")
        print(f"Net Balance:     ₱{balance['net_balance']:.2f}")
        
        if balance['net_balance'] > 0:
            print("Status: Good. Save more!")
        elif balance['net_balance'] < 0:
            print("Status: ALERT!!!. YOU'RE OUT OF BALANCE!!!")
        else:
            print("Status: Zero Balance, don't forget to save!")

    def view_upcoming_due_dates(self):
        upcoming_expenses = [plan for plan in self.plans 
                           if plan.record_type == "expense" and plan.due_date]
        
        if not upcoming_expenses:
            print("No upcoming due dates.")
            return

        print("\nUpcoming Due Dates:")
        for expense in sorted(upcoming_expenses, key=lambda x: x.due_date):
            print(f"- {expense.description}: ₱{expense.amount:.2f} due on {expense.due_date}")
    
    def delete_plan(self):
        self.view_plans()
        if not self.plans:
            return

        while True:
            try:
                index = int(input("Enter the number of the plan to delete (or 0 to cancel): ")) - 1
                if index == -1:
                    print("Deletion cancelled.")
                    return
                if 0 <= index < len(self.plans):
                    deleted_plan = self.plans.pop(index)
                    self.trash_bin.append(deleted_plan)
                    self.save_data()

                    print("\n--- Deletion Receipt ---")
                    print(f"Deleted: {deleted_plan.description} (-₱{deleted_plan.amount:.2f})")

                    balance = self.calculate_balance()
                    if balance['net_balance'] > 0:
                        print(f"Remaining Balance: ₱{balance['net_balance']:.2f}")
                    elif balance['net_balance'] < 0:
                        print(f"Remaining Balance: -₱{abs(balance['net_balance']):.2f}")
                    else:
                        print("No Balance Remaining!")
                    break
                else:
                    print("Invalid plan number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def view_trash_bin(self):
        if not self.trash_bin:
            print("Trash bin is empty.")
            return

        print("\n--- Trash Bin ---")
        self.view_plans(self.trash_bin)
        
        while True:
            print("\nOptions:")
            print("1. Restore a specific plan")
            print("2. Restore all plans")
            print("3. Empty trash bin")
            print("4. Back to settings")
            
            choice = input("Enter your choice (1-4): ")

            if choice == '1':
                self.restore_specific_plan()
                break
            elif choice == '2':
                self.plans.extend(self.trash_bin)
                self.trash_bin.clear()
                self.save_data()
                print("All items restored.")
                break
            elif choice == '3':
                confirmation = input("Permanently delete all items in trash? (yes/no): ").lower()
                if confirmation in ['yes', 'y']:
                    self.trash_bin.clear()
                    self.save_data()
                    print("Trash bin emptied.")
                break
            elif choice == '4':
                break
            else:
                print("Invalid choice.")

    def restore_specific_plan(self):
        self.view_plans(self.trash_bin)
        if not self.trash_bin:
            return

        while True:
            try:
                index = int(input("Enter the number of the plan to restore (or 0 to cancel): ")) - 1
                if index == -1:
                    print("Restoration cancelled.")
                    return
                if 0 <= index < len(self.trash_bin):
                    restored_plan = self.trash_bin.pop(index)
                    self.plans.append(restored_plan)
                    self.save_data()
                    print(f"Restored: {restored_plan.description}")
                    break
                else:
                    print("Invalid plan number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def export_data_to_file(self):
        """Export all data (plans and trash) to a JSON file in device storage."""
        try:
            # Construct the data dictionary
            data = {
                'plans': [plan.to_dict() for plan in self.plans],
                'trash_bin': [plan.to_dict() for plan in self.trash_bin]
            }
            
            # Define the filename with the current date
            filename = f"financial_data_export_{datetime.date.today()}.json"
            
            # Determine the path for the file in the device's storage
            file_path = os.path.join(os.getcwd(), filename)  # Saves in the current working directory

            # Write the data to the JSON file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Data exported to {file_path}")
        except Exception as e:
            print(f"Error exporting data: {e}")

    def save_data(self):
        """Save data to JSON file"""
        try:
            data = {
                'plans': [plan.to_dict() for plan in self.plans],
                'trash_bin': [plan.to_dict() for plan in self.trash_bin]
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        """Load data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                self.plans = [FinancialRecord.from_dict(item) for item in data.get('plans', [])]
                self.trash_bin = [FinancialRecord.from_dict(item) for item in data.get('trash_bin', [])]
        except Exception as e:
            print(f"Error loading data: {e}")

def main():
    tracker = FinanceTracker()
    
    while True:
        print("\n" + "="*50)
        print("        PERSONAL FINANCE TRACKER")
        print("="*50)
        print("1. Add Financial Record")
        print("2. View All Records")
        print("3. Balance Report")
        print("4. Upcoming Due Dates")
        print("5. Export Data into File")
        print("6. Settings Board")
        print("7. Exit")
        print("-"*50)

        choice = input("Enter your choice (1-7): ").strip()

        if choice in ("1", "2", "3", "4", "5", "6", "7"):
            if choice == '1':
                tracker.add_plan_interactive()
            elif choice == '2':
                tracker.view_plans()
            elif choice == '3':
                tracker.display_balance_report()
            elif choice == '4':
                tracker.view_upcoming_due_dates()
            elif choice == '5':
                tracker.export_data_to_file()
            elif choice == '6':
                settings_menu(tracker)
            elif choice == '7':
                print("Thank you for using Personal Finance Tracker!")
                break
        else:
            print("Invalid choice. Please try again.")

def settings_menu(tracker):
    while True:
        print("\n--- Settings Board ---")
        print("1. View Trash Bin")
        print("2. Delete a Plan")
        print("3. Return to Main Menu")

        choice = input("Enter your choice (1-3): ").strip()

        if choice in ("1", "2", "3"):
            if choice == '1':
                tracker.view_trash_bin()
            elif choice == '2':
                tracker.delete_plan()
            elif choice == '3':
                break
        else:
            print("Invalid choice. Please try again.")

    def python_sign_probe() -> str:
        """Non-intrusive helper that returns the string 'python'.

        This function exists only to make Python usage explicit inside
        `casinillo_mpft_8.py` (so GitHub Linguist can clearly detect the repo
        language) and does not change program behavior.
        """
        return "python"

if __name__ == "__main__":
    main()