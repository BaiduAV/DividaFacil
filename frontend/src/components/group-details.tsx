import { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import {
  Users,
  ArrowLeft,
  DollarSign,
  Receipt,
  Edit,
  Settings,
  UserPlus,
  Trash,
  AlertTriangle,
  X,
} from "lucide-react";
import { Group, User } from "../services/api";

interface GroupDetailsProps {
  group: Group;
  currentUser: User;
  onBack: () => void;
  onNavigate: (tab: string, groupId?: string) => void;
  onEditGroup: (groupId: string) => void;
  onAddMembers: (groupId: string) => void;
  onDeleteGroup: (groupId: string) => void;
}

export function GroupDetails({
  group,
  currentUser,
  onBack,
  onNavigate,
  onEditGroup,
  onAddMembers,
  onDeleteGroup,
}: GroupDetailsProps) {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const getMembersArray = (members: Record<string, User>): User[] => {
    return Object.values(members || {});
  };

  const isGroupSettled = (): boolean => {
    const MIN_THRESHOLD = 0.01;
    if (!group.balances) return true;
    for (const balance of Object.values(group.balances)) {
      if (Math.abs(balance) >= MIN_THRESHOLD) {
        return false;
      }
    }
    return true;
  };

  const totalSpent = (group.expenses || []).reduce((total, expense) => total + expense.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onBack}
            className="p-2"
          >
            <ArrowLeft className="w-4 h-4" />
          </Button>
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-full bg-primary/10">
              <Users className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">{group.name}</h1>
              <div className="flex items-center gap-4">
                <p className="text-sm text-muted-foreground">
                  {getMembersArray(group.members).length} members
                </p>
                <Badge
                  variant={
                    (group.expenses || []).length > 0 && !isGroupSettled()
                      ? "default"
                      : "secondary"
                  }
                >
                  {(group.expenses || []).length > 0 && !isGroupSettled()
                    ? "Active"
                    : "Settled"}
                </Badge>
                <span className="text-sm text-muted-foreground">•</span>
                <p className="text-sm text-muted-foreground">
                  {(group.expenses || []).length} expenses
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddMembers(group.id)}
          >
            <UserPlus className="w-4 h-4 mr-2" />
            Add Members
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={() => onEditGroup(group.id)}>
                <Edit className="w-4 h-4 mr-2" />
                Edit Group
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {isGroupSettled() ? (
                <DropdownMenuItem 
                  onClick={() => setShowDeleteDialog(true)}
                  className="text-destructive focus:text-destructive"
                >
                  <Trash className="w-4 h-4 mr-2" />
                  Delete Group
                </DropdownMenuItem>
              ) : (
                <DropdownMenuItem disabled>
                  <Trash className="w-4 h-4 mr-2 opacity-50" />
                  Delete Group
                  <span className="ml-auto text-xs text-muted-foreground">Settle debts first</span>
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/20 mx-auto mb-3">
              <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-sm text-muted-foreground mb-1">Total Spent</p>
            <p className="text-2xl font-bold">
              ${totalSpent.toFixed(2)}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/20 mx-auto mb-3">
              <Receipt className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <p className="text-sm text-muted-foreground mb-1">Total Expenses</p>
            <p className="text-2xl font-bold">{(group.expenses || []).length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900/20 mx-auto mb-3">
              <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <p className="text-sm text-muted-foreground mb-1">Members</p>
            <p className="text-2xl font-bold">{getMembersArray(group.members).length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Members & Balances */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Members & Balances
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {getMembersArray(group.members).map((member) => {
              const balance = (group.balances && group.balances[member.id]) || 0;
              return (
                <Card key={member.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-primary/10 font-semibold">
                          {member.name.split(' ').map((n: string) => n[0]).join('').toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">{member.name}</p>
                        <p className="text-sm text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div
                        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                          Math.abs(balance) < 0.01
                            ? "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                            : balance >= 0
                              ? "bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400"
                              : "bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400"
                        }`}
                      >
                        {Math.abs(balance) < 0.01
                          ? "Settled"
                          : `${balance >= 0 ? "+" : ""}$${Math.abs(balance).toFixed(2)}`}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {Math.abs(balance) < 0.01
                          ? "No balance"
                          : balance >= 0
                            ? "owed to them"
                            : "they owe"}
                      </p>
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Expenses */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Receipt className="w-5 h-5" />
              Recent Expenses
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate("expenses", group.id)}
            >
              View All
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {(group.expenses || []).length > 0 ? (
            <div className="space-y-4">
              {(group.expenses || []).slice(-5).reverse().map((expense) => {
                const paidByMember = getMembersArray(group.members).find(
                  (m: User) => m.id === expense.paid_by
                );
                return (
                  <Card key={expense.id} className="p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-full bg-primary/10">
                          <Receipt className="w-4 h-4 text-primary" />
                        </div>
                        <div>
                          <p className="font-semibold">{expense.description}</p>
                          <p className="text-sm text-muted-foreground">
                            Paid by {paidByMember?.name || "Unknown"} •{" "}
                            {new Date(expense.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">${expense.amount.toFixed(2)}</p>
                        <Badge variant="outline" className="text-xs">
                          {expense.split_type.toLowerCase()}
                        </Badge>
                      </div>
                    </div>
                  </Card>
                );
              })}
              {(group.expenses || []).length > 5 && (
                <p className="text-center text-sm text-muted-foreground py-2">
                  Showing 5 most recent expenses • {(group.expenses || []).length - 5} more expenses
                </p>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <Receipt className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h4 className="font-semibold mb-2">No expenses yet</h4>
              <p className="text-muted-foreground mb-6">
                Start adding expenses to track group spending
              </p>
              <Button onClick={() => onNavigate("add-expense", group.id)}>
                <DollarSign className="w-4 h-4 mr-2" />
                Add First Expense
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4">
        <Button
          onClick={() => onNavigate("add-expense", group.id)}
          className="flex-1"
          size="lg"
        >
          <DollarSign className="w-4 h-4 mr-2" />
          Add Expense
        </Button>
        <Button
          variant="outline"
          onClick={() => onNavigate("expenses", group.id)}
          className="flex-1"
          size="lg"
        >
          <Receipt className="w-4 h-4 mr-2" />
          All Expenses
        </Button>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteDialog && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowDeleteDialog(false);
            }
          }}
        >
          <div className="rounded-lg shadow-xl w-full max-w-md mx-4 bg-card text-card-foreground border border-border animate-in fade-in-0 zoom-in-95 duration-200">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-lg font-semibold text-destructive">Delete Group</h2>
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-sm hover:bg-muted cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-destructive" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-foreground mb-2">Are you sure?</h3>
                  <p className="text-sm text-muted-foreground">
                    This will permanently delete the group <strong>"{group.name}"</strong> and all its data. 
                    This action cannot be undone.
                  </p>
                </div>
              </div>

              <div className="bg-muted/50 p-4 rounded-lg border">
                <p className="text-sm font-medium text-foreground mb-2">
                  Group Details:
                </p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li className="flex items-center gap-2">
                    <span className="w-1 h-1 bg-muted-foreground rounded-full"></span>
                    {getMembersArray(group.members).length} members
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1 h-1 bg-muted-foreground rounded-full"></span>
                    {group.expenses?.length || 0} expenses
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-1 h-1 bg-muted-foreground rounded-full"></span>
                    Status: {isGroupSettled() ? '✓ Settled' : '⚠ Has outstanding balances'}
                  </li>
                </ul>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowDeleteDialog(false)}
                  className="flex-1 px-4 py-2 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors font-medium cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    onDeleteGroup(group.id);
                    setShowDeleteDialog(false);
                  }}
                  className="flex-1 px-4 py-2 rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90 transition-colors font-medium cursor-pointer"
                >
                  Delete Group
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}