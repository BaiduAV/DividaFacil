from dataclasses import dataclass, field
from typing import Dict, Optional, Union
from datetime import datetime


@dataclass
class User:
    """Represents a user in the Splitwise application."""

    id: str
    name: str
    email: str
    balance: Dict[str, float] = field(default_factory=dict)  # user_id -> amount owed
    notification_preferences: Dict[str, Union[bool, int]] = field(
        default_factory=lambda: {
            "email_overdue": True,
            "email_upcoming": True,
            "days_ahead_reminder": 3,
        }
    )
    password_hash: Optional[str] = None  # For authentication
    reset_token: Optional[str] = None  # For password reset
    reset_token_expiry: Optional[datetime] = None  # Reset token expiration

    def update_balance(self, user_id: str, amount: float):
        """Update the balance with another user.

        Args:
            user_id: ID of the other user
            amount: Positive amount means this user owes the other user
        """
        self.balance[user_id] = self.balance.get(user_id, 0) + amount
