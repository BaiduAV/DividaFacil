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
import { Input } from "./ui/input";
import {
  Users,
  Plus,
  Search,
  MoreVertical,
  DollarSign,
  Calendar,
} from "lucide-react";

export function Groups() {
  const groups = [
    {
      id: 1,
      name: "Weekend Trip",
      description: "Lake house getaway",
      members: [
        { name: "You", initials: "YU", isYou: true },
        { name: "Sarah M.", initials: "SM" },
        { name: "Mike L.", initials: "ML" },
        { name: "Emma K.", initials: "EK" },
      ],
      totalSpent: 1250.0,
      yourShare: 312.5,
      yourBalance: -45.2,
      lastActivity: "2 hours ago",
      settled: false,
      expenses: 8,
    },
    {
      id: 2,
      name: "Dinner Club",
      description: "Monthly food adventures",
      members: [
        { name: "You", initials: "YU", isYou: true },
        { name: "Alex P.", initials: "AP" },
        { name: "Jenny W.", initials: "JW" },
        { name: "Tom R.", initials: "TR" },
        { name: "Lisa M.", initials: "LM" },
        { name: "David K.", initials: "DK" },
      ],
      totalSpent: 684.5,
      yourShare: 114.08,
      yourBalance: 23.6,
      lastActivity: "1 day ago",
      settled: false,
      expenses: 12,
    },
    {
      id: 3,
      name: "Office Lunch",
      description: "Weekly team lunches",
      members: [
        { name: "You", initials: "YU", isYou: true },
        { name: "John D.", initials: "JD" },
        { name: "Susan L.", initials: "SL" },
        { name: "Mark T.", initials: "MT" },
        { name: "Rachel B.", initials: "RB" },
        { name: "Kevin S.", initials: "KS" },
        { name: "Amy C.", initials: "AC" },
        { name: "Steve H.", initials: "SH" },
      ],
      totalSpent: 456.8,
      yourShare: 57.1,
      yourBalance: 12.3,
      lastActivity: "3 days ago",
      settled: false,
      expenses: 6,
    },
    {
      id: 4,
      name: "Europe Trip 2024",
      description: "Summer vacation expenses",
      members: [
        { name: "You", initials: "YU", isYou: true },
        { name: "Sarah M.", initials: "SM" },
        { name: "Mike L.", initials: "ML" },
      ],
      totalSpent: 3250.75,
      yourShare: 1083.58,
      yourBalance: 0.0,
      lastActivity: "2 weeks ago",
      settled: true,
      expenses: 24,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Groups</h1>
          <p className="text-muted-foreground">
            Manage your expense groups
          </p>
        </div>
        <Button className="w-full sm:w-auto">
          <Plus className="w-4 h-4 mr-2" />
          Create Group
        </Button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search groups..."
          className="pl-10"
        />
      </div>

      {/* Groups Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {groups.map((group) => (
          <Card
            key={group.id}
            className="hover:shadow-md transition-shadow cursor-pointer"
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg">
                    {group.name}
                  </CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {group.description}
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

              {/* Members */}
              <div className="flex items-center gap-2 mt-3">
                <div className="flex -space-x-2">
                  {group.members
                    .slice(0, 4)
                    .map((member, index) => (
                      <Avatar
                        key={index}
                        className="w-6 h-6 border-2 border-background"
                      >
                        <AvatarFallback className="text-xs bg-primary/10">
                          {member.initials}
                        </AvatarFallback>
                      </Avatar>
                    ))}
                  {group.members.length > 4 && (
                    <div className="w-6 h-6 rounded-full bg-muted border-2 border-background flex items-center justify-center">
                      <span className="text-xs font-medium">
                        +{group.members.length - 4}
                      </span>
                    </div>
                  )}
                </div>
                <span className="text-sm text-muted-foreground">
                  {group.members.length} members
                </span>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Financial Summary */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Total Spent
                  </p>
                  <p className="font-bold">
                    ${group.totalSpent.toFixed(2)}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Your Share
                  </p>
                  <p className="font-bold">
                    ${group.yourShare.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Balance */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                <span className="text-sm font-medium">
                  Your Balance:
                </span>
                <span
                  className={`font-bold ${
                    group.yourBalance > 0
                      ? "text-green-600"
                      : group.yourBalance < 0
                        ? "text-red-600"
                        : "text-muted-foreground"
                  }`}
                >
                  {group.yourBalance === 0
                    ? "Settled"
                    : `${group.yourBalance > 0 ? "+" : ""}$${Math.abs(group.yourBalance).toFixed(2)}`}
                </span>
              </div>

              {/* Status and Activity */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      group.settled ? "secondary" : "outline"
                    }
                  >
                    {group.settled ? "Settled" : "Active"}
                  </Badge>
                  <span className="text-muted-foreground">
                    {group.expenses} expenses
                  </span>
                </div>
                <span className="text-muted-foreground">
                  {group.lastActivity}
                </span>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-2 pt-2">
                <Button variant="outline" size="sm">
                  <DollarSign className="w-4 h-4 mr-1" />
                  Add Expense
                </Button>
                <Button variant="outline" size="sm">
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State for when there are no groups */}
      {groups.length === 0 && (
        <Card className="text-center py-12">
          <CardContent>
            <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">
              No groups yet
            </h3>
            <p className="text-muted-foreground mb-6">
              Create your first group to start splitting
              expenses with friends
            </p>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Group
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}