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
import { Input } from "./ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  Receipt,
  Plus,
  Search,
  Filter,
  Calendar,
  Users,
  DollarSign,
  MoreVertical,
} from "lucide-react";
import { apiClient, Expense, Group } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

export function Expenses() {
  const { user } = useAuth();
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedGroup, setSelectedGroup] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [expensesData, groupsData] = await Promise.all([
        apiClient.getExpenses(),
        apiClient.getGroups(),
      ]);
      setExpenses(expensesData);
      setGroups(groupsData);
    } catch (error) {
      toast.error("Failed to load expenses");
      console.error("Load expenses error:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredExpenses = expenses.filter((expense) => {
    const matchesSearch = expense.description
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesGroup = selectedGroup === "all" || getExpenseGroup(expense)?.id === selectedGroup;
    const matchesCategory = selectedCategory === "all";
    return matchesSearch && matchesGroup && matchesCategory;
  });

  const getExpenseGroup = (expense: Expense) => {
    // Find which group this expense belongs to
    return groups.find(group => 
      group.expenses?.some(e => e.id === expense.id)
    );
  };

  const getExpensePayer = (expense: Expense) => {
    const group = getExpenseGroup(expense);
    if (!group) return null;
    
    const payer = Object.values(group.members).find(member => member.id === expense.paid_by);
    return payer || null;
  };

  const getYourShare = (expense: Expense) => {
    if (!user) return 0;
    
    const group = getExpenseGroup(expense);
    if (!group) return 0;
    
    // Calculate share based on split type
    if (expense.split_type === 'EQUAL') {
      return expense.amount / expense.split_among.length;
    } else if (expense.split_values && expense.split_among.includes(user.id)) {
      const userIndex = expense.split_among.indexOf(user.id);
      if (expense.split_type === 'EXACT') {
        return expense.split_values[userIndex];
      } else if (expense.split_type === 'PERCENTAGE') {
        return (expense.amount * expense.split_values[userIndex]) / 100;
      }
    }
    
    return 0;
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInHours = diffInMs / (1000 * 60 * 60);
    const diffInDays = diffInHours / 24;
    
    if (diffInHours < 1) {
      return `${Math.floor(diffInMs / (1000 * 60))} minutes ago`;
    } else if (diffInDays < 1) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else if (diffInDays < 7) {
      return `${Math.floor(diffInDays)} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const getExpenseStatus = (expense: Expense) => {
    // For now, assume all expenses are unsettled
    // TODO: Add settlement logic when available in API
    return "unsettled";
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "Food & Drink":
        return "🍽️";
      case "Transportation":
        return "🚗";
      case "Accommodation":
        return "🏨";
      case "Entertainment":
        return "🎬";
      default:
        return "💰";
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "Food & Drink":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300";
      case "Transportation":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300";
      case "Accommodation":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300";
      case "Entertainment":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Expenses</h1>
          <p className="text-muted-foreground">
            Track and manage all expenses
          </p>
        </div>
        <Button className="w-full sm:w-auto">
          <Plus className="w-4 h-4 mr-2" />
          Add Expense
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search expenses..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select
              value={selectedGroup}
              onValueChange={setSelectedGroup}
            >
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Groups" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Groups</SelectItem>
                {groups.map((group) => (
                  <SelectItem key={group.id} value={group.id}>
                    {group.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">
                  All Categories
                </SelectItem>
                <SelectItem value="food">
                  Food & Drink
                </SelectItem>
                <SelectItem value="transport">
                  Transportation
                </SelectItem>
                <SelectItem value="accommodation">
                  Accommodation
                </SelectItem>
                <SelectItem value="entertainment">
                  Entertainment
                </SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="icon">
              <Filter className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Expenses List */}
      <div className="space-y-4">
        {filteredExpenses.map((expense) => {
          const group = getExpenseGroup(expense);
          const payer = getExpensePayer(expense);
          const yourShare = getYourShare(expense);
          const timeAgo = getTimeAgo(expense.created_at);
          const status = getExpenseStatus(expense);
          
          return (
            <Card
              key={expense.id}
              className="hover:shadow-md transition-shadow"
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    {/* Category Icon - Default for now since category not in API */}
                    <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center text-lg">
                      💰
                    </div>

                    {/* Expense Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium truncate">
                          {expense.description}
                        </h3>
                        <Badge className="text-xs bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300">
                          General
                        </Badge>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {group?.name || "Unknown Group"}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {timeAgo}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        {payer && (
                          <Avatar className="w-6 h-6">
                            <AvatarFallback className="text-xs">
                              {payer.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                        )}
                        <span className="text-sm text-muted-foreground">
                          Paid by{" "}
                          {payer?.id === user?.id
                            ? "You"
                            : payer?.name || "Unknown"}
                        </span>
                        <Badge
                          variant={status === "settled" ? "secondary" : "outline"}
                          className="text-xs"
                        >
                          {status === "settled" ? "Settled" : "Unsettled"}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Amount and Actions */}
                  <div className="text-right">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="text-right">
                        <p className="font-bold text-lg">
                          ${expense.amount.toFixed(2)}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Your share: ${yourShare.toFixed(2)}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="p-1 h-auto"
                      >
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Split Details */}
                <div className="mt-4 pt-4 border-t border-border">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">
                      Split {expense.split_type.toLowerCase()} among {expense.split_among.length} people
                    </span>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        Edit Split
                      </Button>
                      {status === "unsettled" && (
                        <Button size="sm">
                          <DollarSign className="w-3 h-3 mr-1" />
                          Settle
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Empty State */}
      {expenses.length === 0 && (
        <Card className="text-center py-12">
          <CardContent>
            <Receipt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">
              No expenses yet
            </h3>
            <p className="text-muted-foreground mb-6">
              Start adding expenses to track your shared costs
            </p>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Expense
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Load More */}
      {expenses.length > 0 && (
        <div className="text-center pt-4">
          <Button variant="outline">Load More Expenses</Button>
        </div>
      )}
    </div>
  );
}