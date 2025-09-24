"""CLI application for DividaFacil expense splitting."""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from src.models.user import User
from src.models.group import Group
from src.models.expense import Expense
from src.services.expense_service import ExpenseService, ExpenseCalculationError
from src.constants import (
    SPLIT_EQUAL, SPLIT_EXACT, SPLIT_PERCENTAGE,
    CLI_PROMPT_COLOR, CLI_ERROR_COLOR, CLI_SUCCESS_COLOR, CLI_WARNING_COLOR
)

console = Console()

class CLIError(Exception):
    """Base exception for CLI operations."""
    pass

class MenuOption:
    """Represents a menu option with its handler."""

    def __init__(self, label: str, handler, requires_group: bool = False):
        self.label = label
        self.handler = handler
        self.requires_group = requires_group

class SplitwiseApp:
    """Main CLI application for expense splitting."""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.current_user: Optional[User] = None
        self.current_group: Optional[Group] = None
        self._setup_menu()

    def _setup_menu(self):
        """Setup main menu options."""
        self.menu_options = {
            "1": MenuOption("Create Group", self.create_group_flow),
            "2": MenuOption("Add Expense", self.add_expense_flow, requires_group=True),
            "3": MenuOption("View Balances", self.show_balances, requires_group=True),
            "4": MenuOption("Settle Up", self.show_settle_up, requires_group=True),
            "5": MenuOption("Exit", self.exit_app),
        }

    def initialize_test_user(self) -> None:
        """Create a test user for CLI demo purposes."""
        test_user = self.create_user("Test User", "test@example.com")
        self.current_user = test_user
        console.print(f"[{CLI_SUCCESS_COLOR}]Logged in as: {test_user.name}[/{CLI_SUCCESS_COLOR}]")

    def create_user(self, name: str, email: str) -> User:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        user = User(id=user_id, name=name, email=email)
        self.users[user_id] = user
        return user

    def create_group_flow(self) -> None:
        """Handle group creation workflow."""
        try:
            if not self.current_user:
                self._show_error("Please log in first.")
                return

            group_name = Prompt.ask("Enter group name")
            group = self._create_group(group_name)

            if group:
                self.current_group = group
                self._show_success(f"Group '{group_name}' created and selected!")

        except Exception as e:
            self._show_error(f"Error creating group: {str(e)}")

    def _create_group(self, name: str) -> Optional[Group]:
        """Create a new group."""
        if not self.current_user:
            raise CLIError("No user logged in")

        group_id = str(uuid.uuid4())
        group = Group(id=group_id, name=name)
        group.add_member(self.current_user)
        self.groups[group_id] = group
        return group

    def add_expense_flow(self) -> None:
        """Handle expense addition workflow."""
        try:
            if not self._validate_group_selected():
                return

            expense_data = self._collect_expense_data()
            if not expense_data:
                return

            self._create_and_add_expense(expense_data)

        except ExpenseCalculationError as e:
            self._show_error(f"Calculation error: {str(e)}")
        except Exception as e:
            self._show_error(f"Error adding expense: {str(e)}")

    def _collect_expense_data(self) -> Optional[Dict]:
        """Collect expense data from user input."""
        try:
            amount = float(Prompt.ask("Enter amount"))
            description = Prompt.ask("Enter description")

            split_type = self._get_split_type()
            if not split_type:
                return None

            selected_users = self._select_users()
            if not selected_users:
                return None

            split_values = self._get_split_values(split_type, selected_users)

            return {
                'amount': amount,
                'description': description,
                'split_type': split_type,
                'selected_users': selected_users,
                'split_values': split_values
            }

        except (ValueError, KeyError) as e:
            self._show_error(f"Invalid input: {str(e)}")
            return None

    def _get_split_type(self) -> Optional[str]:
        """Get split type from user."""
        console.print("\n[bold]Split type:[/bold]")
        console.print("1. EQUAL (split equally among selected users)")
        console.print("2. EXACT (specify exact amounts)")
        console.print("3. PERCENTAGE (specify percentages)")

        split_choice = Prompt.ask("Choose split type", choices=["1", "2", "3"])

        split_map = {
            "1": SPLIT_EQUAL,
            "2": SPLIT_EXACT,
            "3": SPLIT_PERCENTAGE
        }

        return split_map.get(split_choice)

    def _select_users(self) -> Optional[List[User]]:
        """Allow user to select users for expense splitting."""
        if not self.current_group:
            return None

        users = list(self.current_group.members.values())

        console.print("\n[bold]Available users:[/bold]")
        for i, user in enumerate(users, 1):
            console.print(f"{i}. {user.name}")

        try:
            selected_indices = Prompt.ask(
                "Select users to split with (comma-separated numbers)"
            ).split(',')

            return [users[int(i.strip()) - 1] for i in selected_indices]
        except (ValueError, IndexError):
            self._show_error("Invalid user selection")
            return None

    def _get_split_values(self, split_type: str, selected_users: List[User]) -> Dict:
        """Get split values based on split type."""
        if split_type == SPLIT_EQUAL:
            return {}
        elif split_type == SPLIT_EXACT:
            return self._get_exact_amounts(selected_users)
        elif split_type == SPLIT_PERCENTAGE:
            return self._get_percentage_amounts(selected_users)
        else:
            return {}

    def _get_exact_amounts(self, selected_users: List[User]) -> Dict[str, float]:
        """Get exact amounts for each user."""
        split_values = {}
        for user in selected_users:
            try:
                value = float(Prompt.ask(f"Amount for {user.name}"))
                split_values[user.id] = value
            except ValueError:
                self._show_error(f"Invalid amount for {user.name}")
                return {}
        return split_values

    def _get_percentage_amounts(self, selected_users: List[User]) -> Dict[str, float]:
        """Get percentage amounts for each user."""
        split_values = {}
        total_percentage = 0.0

        for user in selected_users:
            try:
                percentage = float(Prompt.ask(f"Percentage for {user.name}"))
                split_values[user.id] = percentage
                total_percentage += percentage
            except ValueError:
                self._show_error(f"Invalid percentage for {user.name}")
                return {}

        if abs(total_percentage - 100.0) > 0.01:
            self._show_warning(f"Percentages add up to {total_percentage}%, not 100%")

        return split_values

    def _create_and_add_expense(self, expense_data: Dict) -> None:
        """Create and add expense to the current group."""
        expense_id = str(uuid.uuid4())

        expense = Expense(
            id=expense_id,
            amount=expense_data['amount'],
            description=expense_data['description'],
            paid_by=self.current_user.id,
            split_among=[u.id for u in expense_data['selected_users']],
            split_type=expense_data['split_type'],
            split_values=expense_data['split_values'],
            created_at=datetime.now()
        )
        
        self.current_group.add_expense(expense)
        ExpenseService.calculate_balances(expense, self.current_group.members)
        self._show_success(f"Expense '{expense_data['description']}' added successfully!")

    def show_balances(self) -> None:
        """Show balances for the current group."""
        if not self._validate_group_selected():
            return
            
        table = Table(title=f"Balances for {self.current_group.name}")
        table.add_column("User", style="cyan")
        table.add_column("Net Balance", style="green")
        
        has_balances = False
        for user in self.current_group.members.values():
            net_balance = sum(user.balance.values())
            if abs(net_balance) > 0.01:  # Only show non-zero balances
                has_balances = True
                status = "owes" if net_balance < 0 else "is owed"
                amount = abs(round(net_balance, 2))
                table.add_row(
                    user.name,
                    f"{status} ${amount:.2f}"
                )

        if has_balances:
            console.print(table)
        else:
            console.print(f"[{CLI_SUCCESS_COLOR}]All balances are settled![/{CLI_SUCCESS_COLOR}]")

    def show_settle_up(self) -> None:
        """Show simplified transactions to settle up all balances."""
        if not self._validate_group_selected():
            return
            
        try:
            transactions = ExpenseService.simplify_balances(self.current_group.members)

            if not transactions:
                console.print(f"[{CLI_SUCCESS_COLOR}]No balances to settle![/{CLI_SUCCESS_COLOR}]")
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

        except ExpenseCalculationError as e:
            self._show_error(f"Error calculating settlements: {str(e)}")

    def _validate_group_selected(self) -> bool:
        """Validate that a group is currently selected."""
        if not self.current_group:
            self._show_error("No group selected. Please create a group first.")
            return False
        return True

    def exit_app(self) -> None:
        """Exit the application."""
        console.print(f"[{CLI_WARNING_COLOR}]Goodbye![/{CLI_WARNING_COLOR}]")
        exit(0)

    def _show_error(self, message: str) -> None:
        """Display error message."""
        console.print(f"[{CLI_ERROR_COLOR}]Error: {message}[/{CLI_ERROR_COLOR}]")

    def _show_success(self, message: str) -> None:
        """Display success message."""
        console.print(f"[{CLI_SUCCESS_COLOR}]{message}[/{CLI_SUCCESS_COLOR}]")

    def _show_warning(self, message: str) -> None:
        """Display warning message."""
        console.print(f"[{CLI_WARNING_COLOR}]Warning: {message}[/{CLI_WARNING_COLOR}]")

    def run(self) -> None:
        """Run the main application loop."""
        console.print(Panel("[bold blue]Welcome to DividaFácil CLI![/bold blue]", expand=False))

        self.initialize_test_user()

        while True:
            try:
                self._show_main_menu()
                choice = Prompt.ask("Choose an option", choices=list(self.menu_options.keys()))

                option = self.menu_options[choice]

                # Check if group is required but not selected
                if option.requires_group and not self.current_group:
                    self._show_error("This option requires a group to be selected.")
                    continue

                option.handler()

            except KeyboardInterrupt:
                console.print(f"\n[{CLI_WARNING_COLOR}]Goodbye![/{CLI_WARNING_COLOR}]")
                break
            except Exception as e:
                self._show_error(f"Unexpected error: {str(e)}")

    def _show_main_menu(self) -> None:
        """Display the main menu."""
        console.print("\n[bold]Main Menu:[/bold]")
        for key, option in self.menu_options.items():
            console.print(f"{key}. {option.label}")

        if self.current_group:
            console.print(f"\n[dim]Current group: {self.current_group.name}[/dim]")

def main():
    """Main entry point for the CLI application."""
    app = SplitwiseApp()
    app.run()

if __name__ == "__main__":
    main()
