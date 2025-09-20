#!/usr/bin/env python3
"""
DividaFacil Notification Manager

CLI tool to manage installment payment notifications and send reminders.
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path for module imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.notification_service import NotificationService
from src.services.database_service import DatabaseService
from src.state import GROUPS


def setup_notification_service() -> NotificationService:
    """Setup notification service with SMTP configuration from environment."""
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    return NotificationService(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password
    )


def cmd_check_overdue(args):
    """Check for overdue installments and optionally send notifications."""
    notification_service = setup_notification_service()
    groups = dict(GROUPS.items())  # Convert to regular dict
    
    if args.report_only:
        notification_service.print_overdue_report(groups)
    else:
        sent_count = notification_service.send_overdue_notifications(groups)
        print(f"📧 Enviadas {sent_count} notificações de parcelas em atraso.")
        
        if args.verbose:
            notification_service.print_overdue_report(groups)


def cmd_check_upcoming(args):
    """Check for upcoming installments and optionally send notifications."""
    notification_service = setup_notification_service()
    groups = dict(GROUPS.items())  # Convert to regular dict
    
    upcoming_items = notification_service.get_upcoming_installments(groups, args.days)
    
    if args.report_only:
        if not upcoming_items:
            print(f"✅ Nenhuma parcela vencendo nos próximos {args.days} dias!")
        else:
            print(f"📋 Parcelas vencendo nos próximos {args.days} dias:\n")
            
            # Group by user for better readability
            user_upcoming = {}
            for item in upcoming_items:
                user_id = item.user.id
                if user_id not in user_upcoming:
                    user_upcoming[user_id] = []
                user_upcoming[user_id].append(item)
            
            for user_id, items in user_upcoming.items():
                user = items[0].user
                print(f"👤 {user.name} ({user.email}):")
                for item in items:
                    days_until = -item.days_overdue  # Convert back to positive
                    print(f"   • {item.expense.description} - {item.group.name}")
                    print(f"     Parcela {item.installment.number}: R$ {item.installment.amount:.2f}")
                    if days_until == 0:
                        print(f"     Vence hoje! ({item.installment.due_date.strftime('%d/%m/%Y')})")
                    else:
                        print(f"     Vence em {days_until} dias ({item.installment.due_date.strftime('%d/%m/%Y')})")
                print()
    else:
        sent_count = notification_service.send_upcoming_notifications(groups, args.days)
        print(f"📧 Enviadas {sent_count} notificações de parcelas vencendo.")
        
        if args.verbose:
            if not upcoming_items:
                print(f"✅ Nenhuma parcela vencendo nos próximos {args.days} dias!")


def cmd_test_email(args):
    """Test email configuration by sending a test message."""
    notification_service = setup_notification_service()
    
    subject = "Teste - DividaFacil Notifications"
    body = """Este é um email de teste do sistema de notificações do DividaFacil.

Se você recebeu este email, a configuração SMTP está funcionando corretamente.

Atenciosamente,
Sistema de Notificações DividaFacil"""

    success = notification_service.send_email_notification(args.email, subject, body)
    
    if success:
        print(f"✅ Email de teste enviado com sucesso para {args.email}")
    else:
        print(f"❌ Falha ao enviar email de teste para {args.email}")
        print("Verifique as configurações SMTP nas variáveis de ambiente:")
        print("- SMTP_SERVER")
        print("- SMTP_PORT (opcional, padrão 587)")
        print("- SMTP_USERNAME")  
        print("- SMTP_PASSWORD")


def main():
    parser = argparse.ArgumentParser(
        description="DividaFacil Notification Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check overdue installments and send notifications
  python notifications.py overdue
  
  # Just report overdue installments without sending emails
  python notifications.py overdue --report-only
  
  # Check installments due in next 7 days
  python notifications.py upcoming --days 7
  
  # Test email configuration
  python notifications.py test-email user@example.com
  
Environment Variables:
  SMTP_SERVER      SMTP server hostname
  SMTP_PORT        SMTP server port (default: 587)
  SMTP_USERNAME    SMTP username for authentication
  SMTP_PASSWORD    SMTP password for authentication
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Overdue command
    parser_overdue = subparsers.add_parser('overdue', help='Check and notify about overdue installments')
    parser_overdue.add_argument('--report-only', action='store_true',
                               help='Only show report, do not send notifications')
    parser_overdue.add_argument('--verbose', '-v', action='store_true',
                               help='Show detailed report after sending notifications')
    parser_overdue.set_defaults(func=cmd_check_overdue)
    
    # Upcoming command
    parser_upcoming = subparsers.add_parser('upcoming', help='Check and notify about upcoming installments')
    parser_upcoming.add_argument('--days', type=int, default=3,
                                help='Number of days ahead to check (default: 3)')
    parser_upcoming.add_argument('--report-only', action='store_true',
                                help='Only show report, do not send notifications')
    parser_upcoming.add_argument('--verbose', '-v', action='store_true',
                                help='Show detailed report after sending notifications')
    parser_upcoming.set_defaults(func=cmd_check_upcoming)
    
    # Test email command
    parser_test = subparsers.add_parser('test-email', help='Test email configuration')
    parser_test.add_argument('email', help='Email address to send test message to')
    parser_test.set_defaults(func=cmd_test_email)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args) or 0
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())