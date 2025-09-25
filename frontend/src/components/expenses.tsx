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

export function Expenses() {
  const expenses = [
    {
      id: 1,
      description: "Hotel Stay - Grand Plaza",
      amount: 450.0,
      category: "Accommodation",
      paidBy: { name: "Sarah M.", initials: "SM" },
      group: "Weekend Trip",
      date: "2024-09-20",
      timeAgo: "2 hours ago",
      yourShare: 112.5,
      participants: 4,
      status: "unsettled",
    },
    {
      id: 2,
      description: "Dinner at Romano's",
      amount: 89.5,
      category: "Food & Drink",
      paidBy: { name: "You", initials: "YU", isYou: true },
      group: "Dinner Club",
      date: "2024-09-19",
      timeAgo: "1 day ago",
      yourShare: 14.92,
      participants: 6,
      status: "settled",
    },
    {
      id: 3,
      description: "Uber to Airport",
      amount: 24.8,
      category: "Transportation",
      paidBy: { name: "Mike L.", initials: "ML" },
      group: "Weekend Trip",
      date: "2024-09-18",
      timeAgo: "2 days ago",
      yourShare: 6.2,
      participants: 4,
      status: "unsettled",
    },
    {
      id: 4,
      description: "Groceries for BBQ",
      amount: 156.3,
      category: "Food & Drink",
      paidBy: { name: "Emma K.", initials: "EK" },
      group: "Weekend Trip",
      date: "2024-09-17",
      timeAgo: "3 days ago",
      yourShare: 39.08,
      participants: 4,
      status: "unsettled",
    },
    {
      id: 5,
      description: "Gas for Road Trip",
      amount: 78.45,
      category: "Transportation",
      paidBy: { name: "You", initials: "YU", isYou: true },
      group: "Weekend Trip",
      date: "2024-09-17",
      timeAgo: "3 days ago",
      yourShare: 19.61,
      participants: 4,
      status: "unsettled",
    },
    {
      id: 6,
      description: "Team Lunch - Pizza Palace",
      amount: 94.2,
      category: "Food & Drink",
      paidBy: { name: "John D.", initials: "JD" },
      group: "Office Lunch",
      date: "2024-09-16",
      timeAgo: "4 days ago",
      yourShare: 11.78,
      participants: 8,
      status: "settled",
    },
  ];

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
              />
            </div>
            <Select>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Groups" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Groups</SelectItem>
                <SelectItem value="weekend-trip">
                  Weekend Trip
                </SelectItem>
                <SelectItem value="dinner-club">
                  Dinner Club
                </SelectItem>
                <SelectItem value="office-lunch">
                  Office Lunch
                </SelectItem>
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
        {expenses.map((expense) => (
          <Card
            key={expense.id}
            className="hover:shadow-md transition-shadow"
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  {/* Category Icon */}
                  <div className="w-12 h-12 rounded-lg bg-muted flex items-center justify-center text-lg">
                    {getCategoryIcon(expense.category)}
                  </div>

                  {/* Expense Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium truncate">
                        {expense.description}
                      </h3>
                      <Badge
                        className={`text-xs ${getCategoryColor(expense.category)}`}
                      >
                        {expense.category}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                      <span className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        {expense.group}
                      </span>
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {expense.timeAgo}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Avatar className="w-6 h-6">
                        <AvatarFallback className="text-xs">
                          {expense.paidBy.initials}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-sm text-muted-foreground">
                        Paid by{" "}
                        {expense.paidBy.isYou
                          ? "You"
                          : expense.paidBy.name}
                      </span>
                      <Badge
                        variant={
                          expense.status === "settled"
                            ? "secondary"
                            : "outline"
                        }
                        className="text-xs"
                      >
                        {expense.status === "settled"
                          ? "Settled"
                          : "Unsettled"}
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
                        Your share: $
                        {expense.yourShare.toFixed(2)}
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
                    Split equally among {expense.participants}{" "}
                    people
                  </span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      Edit Split
                    </Button>
                    {expense.status === "unsettled" && (
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
        ))}
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