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

export function Dashboard() {
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
        if (user && group.balances[user.id]) {
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

  // Mock data for recent expenses (will be replaced with API call)
  const recentExpenses = [
    {
      id: "1",
      description: "Hotel Stay",
      amount: 450.0,
      paidBy: "Sarah M.",
      group: "Weekend Trip",
      date: "2 hours ago",
    },
    {
      id: "2",
      description: "Dinner at Romano's",
      amount: 89.5,
      paidBy: "You",
      group: "Dinner Club",
      date: "1 day ago",
    },
    {
      id: "3",
      description: "Uber Ride",
      amount: 24.8,
      paidBy: "Mike L.",
      group: "Office Lunch",
      date: "2 days ago",
    },
  ];

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
              $800.00
            </div>
            <p className="text-xs text-muted-foreground">
              3 installment payments
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
            >
              <Plus className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span className="text-sm">Add Expense</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 hover:border-teal-300 dark:hover:border-teal-700"
            >
              <Users className="w-5 h-5 text-teal-600 dark:text-teal-400" />
              <span className="text-sm">Create Group</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 hover:border-green-300 dark:hover:border-green-700"
            >
              <DollarSign className="w-5 h-5 text-green-600 dark:text-green-400" />
              <span className="text-sm">Settle Up</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col gap-2 gradient-card border-purple-200 dark:border-purple-700"
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
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {groups.slice(0, 3).map((group) => (
            <div
              key={group.id}
              className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h4 className="font-medium">{group.name}</h4>
                  <p className="text-sm text-muted-foreground">
                    {Object.keys(group.members).length} members • $
                    {group.expenses.reduce((sum, exp) => sum + exp.amount, 0).toFixed(2)} total
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-medium">
                  ${user && group.balances[user.id] ? Math.abs(group.balances[user.id]).toFixed(2) : '0.00'}
                </p>
                <Badge
                  variant={
                    (user && group.balances[user.id] && group.balances[user.id] === 0) ? "secondary" : "outline"
                  }
                  className="text-xs"
                >
                  {(user && group.balances[user.id] && group.balances[user.id] === 0) ? "Settled" : "Active"}
                </Badge>
              </div>
            </div>
          ))}
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
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            {
              id: 1,
              planName: "Europe Trip 2025",
              amount: 250.0,
              dueDate: "Dec 1, 2024",
              daysUntilDue: 10,
              group: "Travel Buddies",
              installmentNumber: 3,
              totalInstallments: 6,
              status: "upcoming",
            },
            {
              id: 2,
              planName: "Shared Apartment Rent",
              amount: 300.0,
              dueDate: "Jan 1, 2025",
              daysUntilDue: 41,
              group: "Roommates",
              installmentNumber: 4,
              totalInstallments: 6,
              status: "upcoming",
            },
            {
              id: 3,
              planName: "Car Purchase",
              amount: 250.0,
              dueDate: "Jan 1, 2025",
              daysUntilDue: 41,
              group: "Car Pool",
              installmentNumber: 7,
              totalInstallments: 12,
              status: "upcoming",
            },
          ].map((installment) => (
            <div
              key={installment.id}
              className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
                  <Clock className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <h4 className="font-medium">
                    {installment.planName}
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    {installment.group} •{" "}
                    {installment.installmentNumber}/
                    {installment.totalInstallments}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Due {installment.dueDate} •{" "}
                    {installment.daysUntilDue} days
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-medium">
                  ${installment.amount.toFixed(2)}
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  className="mt-1"
                >
                  Pay Now
                </Button>
              </div>
            </div>
          ))}
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
          >
            View All
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {recentExpenses.map((expense) => (
            <div
              key={expense.id}
              className="flex items-center justify-between p-4 border border-border rounded-lg"
            >
              <div className="flex items-center gap-3">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="text-xs">
                    {expense.paidBy === "You"
                      ? "YU"
                      : expense.paidBy.slice(0, 2)}
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
          ))}
        </CardContent>
      </Card>
    </div>
  );
}