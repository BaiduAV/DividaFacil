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
import { Input } from "./ui/input";
import {
  Users,
  Plus,
  Search,
  MoreVertical,
  DollarSign,
  Calendar,
} from "lucide-react";
import { apiClient, Group } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

export function Groups() {
  const { user } = useAuth();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [showCreateGroup, setShowCreateGroup] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const userGroups = await apiClient.getGroups();
      setGroups(userGroups);
    } catch (error) {
      toast.error("Failed to load groups");
      console.error("Groups error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) {
      toast.error("Please enter a group name");
      return;
    }

    try {
      setCreating(true);
      await apiClient.createGroup({ name: newGroupName.trim() });
      toast.success("Group created successfully!");
      setNewGroupName("");
      setShowCreateGroup(false);
      loadGroups(); // Refresh the list
    } catch (error) {
      toast.error("Failed to create group");
      console.error("Create group error:", error);
    } finally {
      setCreating(false);
    }
  };

  const filteredGroups = groups.filter(group =>
    group.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
        <Button 
          className="w-full sm:w-auto"
          onClick={() => setShowCreateGroup(true)}
        >
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
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Create Group Form */}
      {showCreateGroup && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Group</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateGroup} className="space-y-4">
              <div>
                <label htmlFor="groupName" className="text-sm font-medium">
                  Group Name
                </label>
                <Input
                  id="groupName"
                  placeholder="Enter group name"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  disabled={creating}
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" disabled={creating || !newGroupName.trim()}>
                  {creating ? "Creating..." : "Create Group"}
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    setShowCreateGroup(false);
                    setNewGroupName("");
                  }}
                  disabled={creating}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Groups Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredGroups.map((group) => (
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
                    {Object.keys(group.members).length} members
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
                  {(Array.isArray(group.members) ? group.members : Object.values(group.members || {}))
                    .slice(0, 4)
                    .map((member: any, index) => (
                      <Avatar
                        key={index}
                        className="w-6 h-6 border-2 border-background"
                      >
                        <AvatarFallback className="text-xs bg-primary/10">
                          {member.name?.split(' ').map((n: string) => n[0]).join('').toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    ))}
                  {(Array.isArray(group.members) ? group.members : Object.values(group.members || {})).length > 4 && (
                    <div className="w-6 h-6 rounded-full bg-muted border-2 border-background flex items-center justify-center">
                      <span className="text-xs font-medium">
                        +{(Array.isArray(group.members) ? group.members : Object.values(group.members || {})).length - 4}
                      </span>
                    </div>
                  )}
                </div>
                <span className="text-sm text-muted-foreground">
                  {(Array.isArray(group.members) ? group.members : Object.values(group.members || {})).length} members
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
                    ${(group.expenses || []).reduce((sum, exp) => sum + exp.amount, 0).toFixed(2)}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">
                    Your Balance
                  </p>
                  <p className={`font-bold ${user && group.balances && group.balances[user.id] >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {user && group.balances && group.balances[user.id] >= 0 ? '+' : ''}${user && group.balances ? Math.abs(group.balances[user.id] || 0).toFixed(2) : '0.00'}
                  </p>
                </div>
              </div>

              {/* Status */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      (user && group.balances && group.balances[user.id] === 0) ? "secondary" : "outline"
                    }
                  >
                    {(user && group.balances && group.balances[user.id] === 0) ? "Settled" : "Active"}
                  </Badge>
                  <span className="text-muted-foreground">
                    {(group.expenses || []).length} expense{(group.expenses || []).length !== 1 ? 's' : ''}
                  </span>
                </div>
                <span className="text-muted-foreground">
                  {(group.expenses || []).length > 0 ? 'Recent activity' : 'No expenses yet'}
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