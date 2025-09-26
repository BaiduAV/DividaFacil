import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Users,
  Plus,
  ArrowRight,
  Receipt,
  Calendar,
  Clock,
  CheckCircle,
} from "lucide-react";
import { apiClient, Group, Expense, User } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

interface DashboardProps {
  onNavigate?: (tab: string, openModal?: boolean, groupId?: string) => void;
}

export function Dashboard({ onNavigate }: DashboardProps) {
  const { user } = useAuth();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalBalance, setTotalBalance] = useState(0);
  const [owedAmount, setOwedAmount] = useState(0);
  const [owingAmount, setOwingAmount] = useState(0);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const userGroups = await apiClient.getGroups();

      // Calculate total balance from all groups
      let totalOwed = 0;
      let totalOwing = 0;

      userGroups.forEach(group => {
        if (user && group.balances && group.balances[user.id]) {
          const balance = group.balances[user.id];
          if (balance > 0) {
            totalOwed += balance;
          } else {
            totalOwing += Math.abs(balance);
          }
        }
      });

      setGroups(userGroups);
      setTotalBalance(totalOwed - totalOwing);
      setOwedAmount(totalOwed);
      setOwingAmount(totalOwing);
    } catch (error) {
      toast.error("Failed to load dashboard data");
      console.error("Dashboard error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigateToAddExpense = () => {
    if (onNavigate) {
      onNavigate("add-expense");
    }
  };

  const handleNavigateToGroups = () => {
    if (onNavigate) {
      onNavigate("groups"); // Don't open modal, just navigate to groups
    }
  };

  const handleCreateGroup = () => {
    if (onNavigate) {
      onNavigate("groups", true); // Open create modal
    }
  };

  const handleNavigateToGroup = (groupId: string) => {
    if (onNavigate) {
      onNavigate("group-details", false, groupId);
    }
  };

  const handleNavigateToInstallments = () => {
    if (onNavigate) {
      onNavigate("installments");
    }
  };

  // Get recent expenses from user groups
  const getRecentExpenses = () => {
    const allExpenses: any[] = [];
    
    groups.forEach(group => {
      if (group.expenses && group.expenses.length > 0) {
        group.expenses.forEach(expense => {
          const paidByMember = Array.isArray(group.members) 
            ? group.members.find(m => m.id === expense.paid_by)
            : Object.values(group.members || {}).find((m: any) => m.id === expense.paid_by);
          
          allExpenses.push({
            id: expense.id,
            description: expense.description,
            amount: expense.amount,
            paidBy: user && expense.paid_by === user.id ? "You" : (paidByMember?.name || "Unknown"),
            group: group.name,
            date: new Date(expense.created_at),
            rawDate: expense.created_at
          });
        });
      }
    });

    // Sort by date (newest first) and take first 3
    return allExpenses
      .sort((a, b) => new Date(b.rawDate).getTime() - new Date(a.rawDate).getTime())
      .slice(0, 3)
      .map(expense => ({
        ...expense,
        date: formatRelativeTime(expense.date)
      }));
  };

  // Helper function to format relative time
  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return diffMins <= 1 ? "Just now" : `${diffMins} minutes ago`;
    } else if (diffHours < 24) {
      return diffHours === 1 ? "1 hour ago" : `${diffHours} hours ago`;
    } else {
      return diffDays === 1 ? "1 day ago" : `${diffDays} days ago`;
    }
  };

  const recentExpenses = getRecentExpenses();

  return (
    <div className="space-y-6">
      {/* Balance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Balance
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${totalBalance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {totalBalance >= 0 ? '+' : ''}${Math.abs(totalBalance).toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              {totalBalance >= 0 ? 'You are owed more than you owe' : 'You owe more than you are owed'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              You Are Owed
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${owedAmount.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              From {groups.length} group{groups.length !== 1 ? 's' : ''}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              You Owe
            </CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ${owingAmount.toFixed(2)}
            </div>
            <p className="text-xs text-muted-foreground">
              To settle with others
            </p>
          </CardContent>
        </Card>

        <Card className="gradient-card border-purple-200 dark:border-purple-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              This Month Due
            </CardTitle>
            <Calendar className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-teal-500 bg-clip-text text-transparent">
              $0.00
            </div>
            <p className="text-xs text-muted-foreground">
              No scheduled payments
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 hover:border-purple-300 dark:hover:border-purple-700"
              onClick={handleNavigateToAddExpense}
            >
              <Plus className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span className="text-sm">Add Expense</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 hover:border-teal-300 dark:hover:border-teal-700"
              onClick={handleCreateGroup}
            >
              <Users className="w-5 h-5 text-teal-600 dark:text-teal-400" />
              <span className="text-sm">Create Group</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 hover:border-green-300 dark:hover:border-green-700"
              onClick={() => toast.info("Settlement feature coming soon!")}
            >
              <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
              <span className="text-sm">Settle Up</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 gradient-card border-purple-200 dark:border-purple-700"
              onClick={handleNavigateToInstallments}
            >
              <Calendar className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span className="text-sm">Create Plan</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Recent Groups */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Your Groups</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            className="text-primary"
            onClick={handleNavigateToGroups}
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {groups.length > 0 ? (
            groups.slice(0, 3).map((group) => (
              <div
                key={group.id}
                className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => handleNavigateToGroup(group.id)}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                    <Users className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium">{group.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {(Array.isArray(group.members) ? group.members : Object.values(group.members || {})).length} members • $
                      {(group.expenses || []).reduce((sum, exp) => sum + exp.amount, 0).toFixed(2)} total
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    ${user && group.balances && group.balances[user.id] ? Math.abs(group.balances[user.id]).toFixed(2) : '0.00'}
                  </p>
                  <Badge
                    variant={
                      (user && group.balances && group.balances[user.id] && group.balances[user.id] === 0) ? "secondary" : "outline"
                    }
                    className="text-xs"
                  >
                    {(user && group.balances && group.balances[user.id] && group.balances[user.id] === 0) ? "Settled" : "Active"}
                  </Badge>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-6">
              <Users className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-muted-foreground">No groups yet</p>
              <p className="text-sm text-muted-foreground">
                Create your first group to start splitting expenses
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upcoming Installments */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Upcoming Installments</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            className="text-primary"
            onClick={handleNavigateToInstallments}
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Show empty state for installments since this feature may not be fully implemented */}
          <div className="text-center py-6">
            <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
            <p className="text-muted-foreground">No upcoming installments</p>
            <p className="text-sm text-muted-foreground">
              Create installment plans to track payments over time
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Activity</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            className="text-primary"
            onClick={() => onNavigate && onNavigate("expenses")}
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {recentExpenses.length > 0 ? (
            recentExpenses.map((expense) => (
              <div
                key={expense.id}
                className="flex items-center justify-between p-4 border border-border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="text-xs">
                      {expense.paidBy === "You"
                        ? "YU"
                        : expense.paidBy.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="font-medium">
                      {expense.description}
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Paid by {expense.paidBy} • {expense.group}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">
                    ${expense.amount.toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {expense.date}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-6">
              <Receipt className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
              <p className="text-muted-foreground">No recent expenses</p>
              <p className="text-sm text-muted-foreground">
                Start adding expenses to your groups to see them here
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}