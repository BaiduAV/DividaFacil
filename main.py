import uuid
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

from src.models.user import User
from src.models.group import Group
from src.models.expense import Expense
from src.services.expense_service import ExpenseService

console = Console()

class SplitwiseApp:
    def __init__(self):
        self.users = {}
        self.groups = {}
        self.current_user = None
        self.current_group = None

    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        user = User(id=user_id, name=name, email=email)
        self.users[user_id] = user
        return user

    def create_group(self, name: str) -> Group:
        """Create a new group."""
        if not self.current_user:
            console.print("[red]Please log in first.[/red]")
            return None
            
        group_id = str(uuid.uuid4())
        group = Group(id=group_id, name=name)
        group.add_member(self.current_user)
        self.groups[group_id] = group
        return group

    def add_expense(self, amount: float, description: str, split_type: str, **kwargs):
        """Add an expense to the current group."""
        if not self.current_group:
            console.print("[red]No group selected.[/red]")
            return
            
        expense_id = str(uuid.uuid4())
        paid_by = self.current_user.id
        
        # Get split details based on split type
        if split_type == 'EQUAL':
            split_among = kwargs.get('split_among', [])
        elif split_type == 'EXACT':
            split_among = list(kwargs.get('split_values', {}).keys())
        elif split_type == 'PERCENTAGE':
            split_among = list(kwargs.get('split_percentages', {}).keys())
        else:
            console.print("[red]Invalid split type.[/red]")
            return

        # Create and add the expense
        expense = Expense(
            id=expense_id,
            amount=amount,
            description=description,
            paid_by=paid_by,
            split_among=split_among,
            split_type=split_type,
            split_values=kwargs.get('split_values', {}) if split_type == 'EXACT' else {},
            created_at=datetime.now()
        )
        
        try:
            self.current_group.add_expense(expense)
            ExpenseService.calculate_balances(expense, self.current_group.members)
            console.print(f"[green]Expense '{description}' added successfully![/green]")
        except ValueError as e:
            console.print(f"[red]Error: {str(e)}[/red]")

    def show_balances(self):
        """Show balances for the current group."""
        if not self.current_group:
            console.print("[red]No group selected.[/red]")
            return
            
        table = Table(title=f"Balances for {self.current_group.name}")
        table.add_column("User", style="cyan")
        table.add_column("Net Balance", style="green")
        
        for user in self.current_group.members.values():
            net_balance = sum(user.balance.values())
            if abs(net_balance) > 0.01:  # Only show non-zero balances
                status = "owes" if net_balance < 0 else "is owed"
                amount = abs(round(net_balance, 2))
                table.add_row(
                    user.name,
                    f"{status} ${amount:.2f}"
                )
                
        console.print(table)

    def show_settle_up(self):
        """Show simplified transactions to settle up all balances."""
        if not self.current_group:
            console.print("[red]No group selected.[/red]")
            return
            
        transactions = ExpenseService.simplify_balances(self.current_group.members)
        
        if not transactions:
            console.print("[green]No balances to settle![/green]")
            return
            
        table = Table(title="Settle Up")
        table.add_column("From", style="red")
        table.add_column("To", style="green")
        table.add_column("Amount", style="bold")
        
        for t in transactions:
            from_user = self.users[t['from']].name
            to_user = self.users[t['to']].name
            table.add_row(
                from_user,
                to_user,
                f"${t['amount']:.2f}"
            )
            
        console.print(table)

def main():
    app = SplitwiseApp()
    console.print("[bold blue]Welcome to Splitwise CLI![/bold blue]")
    
    # Create a test user
    test_user = app.create_user("Test User", "test@example.com")
    app.current_user = test_user
    
    while True:
        console.print("\n[bold]Main Menu:[/bold]")
        console.print("1. Create Group")
        console.print("2. Add Expense")
        console.print("3. View Balances")
        console.print("4. Settle Up")
        console.print("5. Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            group_name = Prompt.ask("Enter group name")
            group = app.create_group(group_name)
            if group:
                app.current_group = group
                console.print(f"[green]Group '{group_name}' created and selected![/green]")
                
        elif choice == "2" and app.current_group:
            amount = float(Prompt.ask("Enter amount"))
            description = Prompt.ask("Enter description")
            
            console.print("\nSplit type:")
            console.print("1. EQUAL (split equally among selected users)")
            console.print("2. EXACT (specify exact amounts)")
            console.print("3. PERCENTAGE (specify percentages)")
            
            split_choice = Prompt.ask("Choose split type", choices=["1", "2", "3"])
            
            # Show available users to split with
            users = list(app.current_group.members.values())
            for i, user in enumerate(users, 1):
                console.print(f"{i}. {user.name}")
                
            selected_indices = Prompt.ask(
                "Select users to split with (comma-separated numbers)"
            ).split(',')
            
            selected_users = [users[int(i.strip()) - 1] for i in selected_indices]
            
            if split_choice == "1":  # EQUAL
                app.add_expense(
                    amount=amount,
                    description=description,
                    split_type='EQUAL',
                    split_among=[u.id for u in selected_users]
                )
                
            elif split_choice == "2":  # EXACT
                split_values = {}
                for user in selected_users:
                    value = float(Prompt.ask(f"Amount for {user.name}"))
                    split_values[user.id] = value
                    
                app.add_expense(
                    amount=amount,
                    description=description,
                    split_type='EXACT',
                    split_values=split_values
                )
                
            elif split_choice == "3":  # PERCENTAGE
                split_percentages = {}
                for user in selected_users:
                    percentage = float(Prompt.ask(f"Percentage for {user.name}"))
                    split_percentages[user.id] = percentage
                    
                app.add_expense(
                    amount=amount,
                    description=description,
                    split_type='PERCENTAGE',
                    split_values=split_percentages
                )
                
        elif choice == "3" and app.current_group:
            app.show_balances()
            
        elif choice == "4" and app.current_group:
            app.show_settle_up()
            
        elif choice == "5":
            console.print("[yellow]Goodbye![/yellow]")
            break
            
        else:
            console.print("[red]Invalid option or no group selected.[/red]")

if __name__ == "__main__":
    main()
