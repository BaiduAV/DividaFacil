import logging
import smtplib
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from ..models.expense import Expense
from ..models.group import Group
from ..models.installment import Installment
from ..models.user import User


@dataclass
class OverdueInstallment:
    """Represents an overdue installment for notification purposes."""

    user: User
    expense: Expense
    installment: Installment
    group: Group
    days_overdue: int


class NotificationService:
    """Service for handling installment payment notifications and reminders."""

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port or 587
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.logger = logging.getLogger(__name__)

    def get_overdue_installments(self, groups: Dict[str, Group]) -> List[OverdueInstallment]:
        """Get all overdue installments across all groups.

        Args:
            groups: Dictionary of group_id -> Group objects

        Returns:
            List of OverdueInstallment objects
        """
        overdue = []
        today = date.today()

        for group in groups.values():
            for expense in group.expenses:
                if expense.installments_count <= 1 or not expense.installments:
                    continue

                for installment in expense.installments:
                    # Convert due_date to date for comparison if it's a datetime
                    due_date = installment.due_date
                    if isinstance(due_date, datetime):
                        due_date = due_date.date()

                    if not installment.paid and due_date < today:
                        days_overdue = (today - due_date).days

                        # For each user who owes money for this installment
                        for user_id in expense.split_among:
                            if user_id != expense.paid_by:  # Don't notify the payer
                                user = group.members.get(user_id)
                                if user:
                                    overdue.append(
                                        OverdueInstallment(
                                            user=user,
                                            expense=expense,
                                            installment=installment,
                                            group=group,
                                            days_overdue=days_overdue,
                                        )
                                    )

        return overdue

    def get_upcoming_installments(
        self, groups: Dict[str, Group], days_ahead: int = 3
    ) -> List[OverdueInstallment]:
        """Get installments due in the next few days.

        Args:
            groups: Dictionary of group_id -> Group objects
            days_ahead: Number of days ahead to check for due installments

        Returns:
            List of OverdueInstallment objects (days_overdue will be negative for upcoming)
        """
        upcoming = []
        today = date.today()
        future_date = today + timedelta(days=days_ahead)

        for group in groups.values():
            for expense in group.expenses:
                if expense.installments_count <= 1 or not expense.installments:
                    continue

                for installment in expense.installments:
                    # Convert due_date to date for comparison if it's a datetime
                    due_date = installment.due_date
                    if isinstance(due_date, datetime):
                        due_date = due_date.date()

                    if not installment.paid and today <= due_date <= future_date:
                        days_until_due = (due_date - today).days

                        # For each user who owes money for this installment
                        for user_id in expense.split_among:
                            if user_id != expense.paid_by:  # Don't notify the payer
                                user = group.members.get(user_id)
                                if user:
                                    upcoming.append(
                                        OverdueInstallment(
                                            user=user,
                                            expense=expense,
                                            installment=installment,
                                            group=group,
                                            days_overdue=-days_until_due,  # Negative for upcoming
                                        )
                                    )

        return upcoming

    def send_email_notification(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email notification.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content

        Returns:
            True if email was sent successfully, False otherwise
        """
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            self.logger.warning("SMTP configuration incomplete, skipping email notification")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            self.logger.info(f"Email notification sent to {to_email}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def generate_overdue_notification_text(self, overdue_items: List[OverdueInstallment]) -> str:
        """Generate notification text for overdue installments.

        Args:
            overdue_items: List of overdue installments for a user

        Returns:
            Formatted notification text
        """
        if not overdue_items:
            return ""

        user_name = overdue_items[0].user.name
        text = f"Olá {user_name},\n\n"
        text += "Você possui parcelas em atraso no DividaFacil:\n\n"

        for item in overdue_items:
            due_date = item.installment.due_date
            if isinstance(due_date, datetime):
                due_date = due_date.date()
            text += f"• {item.expense.description} - Grupo: {item.group.name}\n"
            text += f"  Parcela {item.installment.number} de R$ {item.installment.amount:.2f}\n"
            text += f"  Vencimento: {due_date.strftime('%d/%m/%Y')}\n"
            text += f"  {item.days_overdue} dias em atraso\n\n"

        text += "Por favor, acesse o sistema para efetuar o pagamento.\n\n"
        text += "Atenciosamente,\nEquipe DividaFacil"

        return text

    def generate_upcoming_notification_text(self, upcoming_items: List[OverdueInstallment]) -> str:
        """Generate notification text for upcoming installments.

        Args:
            upcoming_items: List of upcoming installments for a user

        Returns:
            Formatted notification text
        """
        if not upcoming_items:
            return ""

        user_name = upcoming_items[0].user.name
        text = f"Olá {user_name},\n\n"
        text += "Você possui parcelas vencendo nos próximos dias no DividaFacil:\n\n"

        for item in upcoming_items:
            days_until = -item.days_overdue  # Convert back to positive
            due_date = item.installment.due_date
            if isinstance(due_date, datetime):
                due_date = due_date.date()
            text += f"• {item.expense.description} - Grupo: {item.group.name}\n"
            text += f"  Parcela {item.installment.number} de R$ {item.installment.amount:.2f}\n"
            text += f"  Vencimento: {due_date.strftime('%d/%m/%Y')}\n"
            if days_until == 0:
                text += "  Vence hoje!\n\n"
            else:
                text += f"  Vence em {days_until} dias\n\n"

        text += "Lembre-se de efetuar o pagamento até a data de vencimento.\n\n"
        text += "Atenciosamente,\nEquipe DividaFacil"

        return text

    def send_overdue_notifications(self, groups: Dict[str, Group]) -> int:
        """Send notifications for all overdue installments.

        Args:
            groups: Dictionary of group_id -> Group objects

        Returns:
            Number of notifications sent
        """
        overdue_items = self.get_overdue_installments(groups)

        # Group by user and filter by preferences
        user_overdue: Dict[str, List[OverdueInstallment]] = {}
        for item in overdue_items:
            user = item.user
            user_id = user.id

            # Check if user wants overdue notifications
            if user.notification_preferences.get("email_overdue", True):
                if user_id not in user_overdue:
                    user_overdue[user_id] = []
                user_overdue[user_id].append(item)

        sent_count = 0
        for _user_id, items in user_overdue.items():
            user = items[0].user
            subject = f"DividaFacil - Parcelas em atraso ({len(items)} pendente{'s' if len(items) > 1 else ''})"
            body = self.generate_overdue_notification_text(items)

            if self.send_email_notification(user.email, subject, body):
                sent_count += 1
            else:
                # Log to console as fallback when email is not configured
                print(f"📬 Console notification for {user.name} ({user.email}):")
                print(f"Subject: {subject}")
                print("---")
                print(body)
                print("=" * 50)
                sent_count += 1  # Count console notifications as sent

        return sent_count

    def send_upcoming_notifications(self, groups: Dict[str, Group], days_ahead: int = 3) -> int:
        """Send notifications for upcoming installments.

        Args:
            groups: Dictionary of group_id -> Group objects
            days_ahead: Number of days ahead to check

        Returns:
            Number of notifications sent
        """
        upcoming_items = self.get_upcoming_installments(groups, days_ahead)

        # Group by user and filter by preferences
        user_upcoming: Dict[str, List[OverdueInstallment]] = {}
        for item in upcoming_items:
            user = item.user
            user_id = user.id

            # Check if user wants upcoming notifications and respects their preferred days ahead
            user_days_ahead = user.notification_preferences.get("days_ahead_reminder", 3)
            if (
                user.notification_preferences.get("email_upcoming", True)
                and -item.days_overdue <= user_days_ahead
            ):  # item.days_overdue is negative for upcoming
                if user_id not in user_upcoming:
                    user_upcoming[user_id] = []
                user_upcoming[user_id].append(item)

        sent_count = 0
        for _user_id, items in user_upcoming.items():
            user = items[0].user
            subject = f"DividaFacil - Parcelas vencendo ({len(items)} próxima{'s' if len(items) > 1 else ''})"
            body = self.generate_upcoming_notification_text(items)

            if self.send_email_notification(user.email, subject, body):
                sent_count += 1
            else:
                # Log to console as fallback when email is not configured
                print(f"📬 Console notification for {user.name} ({user.email}):")
                print(f"Subject: {subject}")
                print("---")
                print(body)
                print("=" * 50)
                sent_count += 1  # Count console notifications as sent

        return sent_count

    def print_overdue_report(self, groups: Dict[str, Group]) -> None:
        """Print a console report of overdue installments."""
        overdue_items = self.get_overdue_installments(groups)

        if not overdue_items:
            print("✅ Nenhuma parcela em atraso encontrada!")
            return

        print(f"⚠️  Encontradas {len(overdue_items)} parcelas em atraso:\n")

        # Group by user for better readability
        user_overdue: Dict[str, List[OverdueInstallment]] = {}
        for item in overdue_items:
            user_id = item.user.id
            if user_id not in user_overdue:
                user_overdue[user_id] = []
            user_overdue[user_id].append(item)

        for _user_id, items in user_overdue.items():
            user = items[0].user
            print(f"👤 {user.name} ({user.email}):")
            for item in items:
                due_date = item.installment.due_date
                if isinstance(due_date, datetime):
                    due_date = due_date.date()
                print(f"   • {item.expense.description} - {item.group.name}")
                print(f"     Parcela {item.installment.number}: R$ {item.installment.amount:.2f}")
                print(
                    f"     Vencimento: {due_date.strftime('%d/%m/%Y')} ({item.days_overdue} dias atraso)"
                )
            print()
