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
import { Label } from "./ui/label";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "./ui/dropdown-menu";
import {
  Users,
  Plus,
  Search,
  MoreVertical,
  DollarSign,
  Calendar,
  Edit,
  Trash,
  UserPlus,
  Settings,
  X,
  Receipt,
  AlertTriangle,
} from "lucide-react";
import { apiClient, Group, User } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

interface GroupsProps {
  openCreateModal?: boolean;
  onCreateModalClose?: () => void;
  onNavigate?: (tab: string, groupId?: string) => void;
  refreshTrigger?: boolean;
}

export function Groups({ openCreateModal = false, onCreateModalClose, onNavigate, refreshTrigger }: GroupsProps) {
  const { user } = useAuth();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [showCreateGroup, setShowCreateGroup] = useState(openCreateModal);
  const [newGroupName, setNewGroupName] = useState("");
  const [creating, setCreating] = useState(false);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<User[]>([]);
  const [memberEmails, setMemberEmails] = useState<string[]>([]);
  const [newMemberEmail, setNewMemberEmail] = useState("");
  const [showGroupDetails, setShowGroupDetails] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [groupToDelete, setGroupToDelete] = useState<Group | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Helper function to convert members dictionary to array
  const getMembersArray = (members: Record<string, User>): User[] => {
    return Object.values(members || {});
  };

  useEffect(() => {
    loadGroups();
    loadUsers();
  }, []);

  // Refresh groups when refreshTrigger changes
  useEffect(() => {
    if (refreshTrigger !== undefined) {
      loadGroups();
    }
  }, [refreshTrigger]);

  const loadUsers = async () => {
    try {
      // Get the current user - for now, this is the only user available due to privacy constraints
      const users = await apiClient.getCurrentUser();
      setAvailableUsers(users);
    } catch (error) {
      console.error("Failed to load users:", error);
      // Fallback to empty array
      setAvailableUsers([]);
    }
  };

  useEffect(() => {
    if (openCreateModal) {
      setShowCreateGroup(true);
      setSelectedUsers([]); // Reset selected users when opening modal
    }
  }, [openCreateModal]);

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

  const handleAddMemberEmail = () => {
    const email = newMemberEmail.trim();
    if (email && !memberEmails.includes(email) && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setMemberEmails([...memberEmails, email]);
      setNewMemberEmail("");
    } else if (!email) {
      toast.error("Please enter an email address");
    } else if (memberEmails.includes(email)) {
      toast.error("Email already added");
    } else {
      toast.error("Please enter a valid email address");
    }
  };

  const handleRemoveMemberEmail = (emailToRemove: string) => {
    setMemberEmails(memberEmails.filter(email => email !== emailToRemove));
  };

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) {
      toast.error("Please enter a group name");
      return;
    }

    try {
      setCreating(true);
      const memberIds = selectedUsers.map(user => user.id);
      await apiClient.createGroup({ 
        name: newGroupName.trim(),
        member_ids: memberIds,
        member_emails: memberEmails
      });
      toast.success("Group created successfully!");
      setNewGroupName("");
      setSelectedUsers([]);
      setMemberEmails([]);
      setNewMemberEmail("");
      setShowCreateGroup(false);
      if (onCreateModalClose) {
        onCreateModalClose();
      }
      loadGroups(); // Refresh the list
    } catch (error) {
      toast.error("Failed to create group");
      console.error("Create group error:", error);
    } finally {
      setCreating(false);
    }
  };

  const handleViewGroupDetails = (groupId: string) => {
    const group = groups.find(g => g.id === groupId);
    if (group) {
      setSelectedGroup(group);
      setShowGroupDetails(true);
    }
  };

  const handleEditGroup = (groupId: string) => {
    toast.info(`Edit group ${groupId} - Coming soon!`);
  };

  const handleAddMembers = (groupId: string) => {
    toast.info(`Add members to group ${groupId} - Coming soon!`);
  };

  const isGroupSettled = (group: Group): boolean => {
    // A group is settled if all members have no significant balances
    const MIN_THRESHOLD = 0.01; // $0.01 minimum threshold
    
    // Check group-level balances
    if (group.balances) {
      for (const balance of Object.values(group.balances)) {
        if (Math.abs(balance) >= MIN_THRESHOLD) {
          return false;
        }
      }
    }
    return true;
  };

  const handleDeleteGroup = (groupId: string) => {
    const group = groups.find(g => g.id === groupId);
    if (!group) {
      toast.error("Group not found");
      return;
    }

    if (!isGroupSettled(group)) {
      toast.error("Cannot delete group with outstanding balances. Please settle all debts first.");
      return;
    }

    setGroupToDelete(group);
    setShowDeleteConfirmation(true);
  };

  const confirmDeleteGroup = async () => {
    if (!groupToDelete) return;

    try {
      setDeleting(true);
      await apiClient.deleteGroup(groupToDelete.id);
      toast.success(`Group "${groupToDelete.name}" deleted successfully!`);
      setShowDeleteConfirmation(false);
      setGroupToDelete(null);
      loadGroups(); // Refresh the list
    } catch (error: any) {
      if (error.status === 400) {
        toast.error("Cannot delete group with outstanding balances. Please settle all debts first.");
      } else if (error.status === 403) {
        toast.error("You don't have permission to delete this group.");
      } else if (error.status === 404) {
        toast.error("Group not found.");
      } else {
        toast.error("Failed to delete group. Please try again.");
      }
      console.error("Delete group error:", error);
    } finally {
      setDeleting(false);
    }
  };

  const handleGroupSettings = (groupId: string) => {
    toast.info(`Group settings for ${groupId} - Coming soon!`);
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
            onClick={() => setShowCreateGroup(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
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
                    {getMembersArray(group.members).length} members
                  </p>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="p-1 h-auto"
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-48">
                    <DropdownMenuItem onClick={() => handleViewGroupDetails(group.id)}>
                      <Settings className="w-4 h-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleEditGroup(group.id)}>
                      <Edit className="w-4 h-4 mr-2" />
                      Edit Group
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleAddMembers(group.id)}>
                      <UserPlus className="w-4 h-4 mr-2" />
                      Add Members
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      onClick={() => handleDeleteGroup(group.id)}
                      className="text-destructive focus:text-destructive"
                    >
                      <Trash className="w-4 h-4 mr-2" />
                      Delete Group
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {/* Members */}
              <div className="flex items-center gap-2 mt-3">
                <div className="flex -space-x-2">
                  {getMembersArray(group.members)
                    .slice(0, 4)
                    .map((member, index) => (
                      <Avatar
                        key={member.id || index}
                        className="w-6 h-6 border-2 border-background"
                      >
                        <AvatarFallback className="text-xs bg-primary/10">
                          {member.name?.split(' ').map((n: string) => n[0]).join('').toUpperCase() || '?'}
                        </AvatarFallback>
                      </Avatar>
                    ))}
                  {getMembersArray(group.members).length > 4 && (
                    <div className="w-6 h-6 rounded-full bg-muted border-2 border-background flex items-center justify-center">
                      <span className="text-xs font-medium">
                        +{getMembersArray(group.members).length - 4}
                      </span>
                    </div>
                  )}
                </div>
                <span className="text-sm text-muted-foreground">
                  {getMembersArray(group.members).length} members
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
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => onNavigate && onNavigate("add-expense", group.id)}
                >
                  <DollarSign className="w-4 h-4 mr-1" />
                  Add Expense
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => handleViewGroupDetails(group.id)}
                >
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
            <Button onClick={() => setShowCreateGroup(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Your First Group
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Create Group Modal */}
      {showCreateGroup && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowCreateGroup(false);
              setNewGroupName("");
              setSelectedUsers([]);
              if (onCreateModalClose) {
                onCreateModalClose();
              }
            }
          }}
        >
          <div 
            className="rounded-lg shadow-lg p-6 w-full max-w-md mx-4 bg-card text-card-foreground border border-border"
          >
            <h2 className="text-xl font-semibold mb-2">
              Create New Group
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Create a new group to split expenses with friends and family.
            </p>
            
            <form onSubmit={handleCreateGroup}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-foreground mb-2">
                  Group Name
                </label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  placeholder="Enter group name..."
                  autoFocus
                  disabled={creating}
                  className="w-full px-3 py-2 rounded-md bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
                />
              </div>

              {/* User Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-foreground mb-2">
                  Add Members (Optional)
                </label>
                <div className="max-h-32 overflow-y-auto rounded-md border border-border bg-muted">
                  {availableUsers.length > 0 ? (
                    availableUsers.map((availableUser) => (
                      <label 
                        key={availableUser.id} 
                        className="flex items-center p-2 cursor-pointer hover:bg-card transition-colors border-b border-border last:border-b-0"
                      >
                        <input
                          type="checkbox"
                          checked={selectedUsers.some(u => u.id === availableUser.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedUsers([...selectedUsers, availableUser]);
                            } else {
                              setSelectedUsers(selectedUsers.filter(u => u.id !== availableUser.id));
                            }
                          }}
                          disabled={creating}
                          className="mr-2 accent-primary"
                        />
                        <div className="flex-1">
                          <div className="text-sm font-medium text-foreground">
                            {availableUser.name}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {availableUser.email}
                          </div>
                        </div>
                      </label>
                    ))
                  ) : (
                    <div className="p-3 text-sm text-center text-muted-foreground">
                      No users available
                    </div>
                  )}
                </div>
                {selectedUsers.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-muted-foreground mb-1">
                      Selected members ({selectedUsers.length}):
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {selectedUsers.map((selectedUser) => (
                        <span 
                          key={selectedUser.id}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-primary/10 text-primary"
                        >
                          {selectedUser.name}
                          <button
                            type="button"
                            onClick={() => setSelectedUsers(selectedUsers.filter(u => u.id !== selectedUser.id))}
                            disabled={creating}
                            className="ml-1 text-primary hover:text-primary/80 disabled:opacity-50"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Email-based Member Addition */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-foreground mb-2">
                  Add Members by Email
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="email"
                    value={newMemberEmail}
                    onChange={(e) => setNewMemberEmail(e.target.value)}
                    placeholder="Enter email address..."
                    disabled={creating}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddMemberEmail();
                      }
                    }}
                    className="flex-1 px-3 py-2 rounded-md bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
                  />
                  <button
                    type="button"
                    onClick={handleAddMemberEmail}
                    disabled={creating || !newMemberEmail.trim()}
                    className="px-3 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Add
                  </button>
                </div>
                {memberEmails.length > 0 && (
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">
                      Member emails ({memberEmails.length}):
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {memberEmails.map((email, index) => (
                        <span 
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-secondary/10 text-secondary-foreground"
                        >
                          {email}
                          <button
                            type="button"
                            onClick={() => handleRemoveMemberEmail(email)}
                            disabled={creating}
                            className="ml-1 text-secondary-foreground hover:text-secondary-foreground/80 disabled:opacity-50"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateGroup(false);
                    setNewGroupName("");
                    setSelectedUsers([]);
                    setMemberEmails([]);
                    setNewMemberEmail("");
                    if (onCreateModalClose) {
                      onCreateModalClose();
                    }
                  }}
                  disabled={creating}
                  className="px-4 py-2 rounded-md bg-background text-foreground border border-border hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={creating || !newGroupName.trim()}
                  className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {creating ? "Creating..." : "Create Group"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Group Details Modal */}
      {showGroupDetails && selectedGroup && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowGroupDetails(false);
              setSelectedGroup(null);
            }
          }}
        >
          <div 
            className="rounded-xl shadow-2xl w-full max-w-4xl bg-card text-card-foreground border border-border max-h-[95vh] overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border bg-gradient-to-r from-primary/5 to-primary/10">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-full bg-primary/10">
                  <Users className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">{selectedGroup.name}</h2>
                  <div className="flex items-center gap-4 mt-1">
                    <p className="text-sm text-muted-foreground">
                      {getMembersArray(selectedGroup.members).length} members
                    </p>
                    <Badge variant={selectedGroup.expenses.length > 0 && Object.values(selectedGroup.balances).some(b => Math.abs(b) >= 0.01) ? "default" : "secondary"}>
                      {selectedGroup.expenses.length > 0 && Object.values(selectedGroup.balances).some(b => Math.abs(b) >= 0.01) ? "Active" : "Settled"}
                    </Badge>
                    <span className="text-sm text-muted-foreground">•</span>
                    <p className="text-sm text-muted-foreground">
                      {selectedGroup.expenses.length} expenses
                    </p>
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setShowGroupDetails(false);
                  setSelectedGroup(null);
                }}
                className="hover:bg-background/80"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {/* Content */}
            <div className="overflow-y-auto max-h-[calc(95vh-80px)]">
              <div className="p-6 space-y-8">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/20 mx-auto mb-2">
                        <DollarSign className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                      </div>
                      <p className="text-sm text-muted-foreground">Total Spent</p>
                      <p className="text-xl font-bold">
                        ${selectedGroup.expenses.reduce((total, expense) => total + expense.amount, 0).toFixed(2)}
                      </p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/20 mx-auto mb-2">
                        <Receipt className="w-5 h-5 text-green-600 dark:text-green-400" />
                      </div>
                      <p className="text-sm text-muted-foreground">Expenses</p>
                      <p className="text-xl font-bold">{selectedGroup.expenses.length}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4 text-center">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/20 mx-auto mb-2">
                        <Users className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                      </div>
                      <p className="text-sm text-muted-foreground">Members</p>
                      <p className="text-xl font-bold">{getMembersArray(selectedGroup.members).length}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Members Section */}
                <div>
                  <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    Members & Balances
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {getMembersArray(selectedGroup.members).map((member) => {
                      const balance = selectedGroup.balances[member.id] || 0;
                      return (
                        <Card key={member.id} className="overflow-hidden">
                          <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <Avatar className="w-10 h-10">
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
                                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                                  Math.abs(balance) < 0.01 
                                    ? 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' 
                                    : balance >= 0 
                                      ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' 
                                      : 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
                                }`}>
                                  {Math.abs(balance) < 0.01 ? 'Settled' : `${balance >= 0 ? '+' : ''}$${Math.abs(balance).toFixed(2)}`}
                                </div>
                                <p className="text-xs text-muted-foreground mt-1">
                                  {Math.abs(balance) < 0.01 ? 'No balance' : balance >= 0 ? 'owed to them' : 'they owe'}
                                </p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </div>

                {/* Recent Expenses Section */}
                <div>
                  <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                    <Receipt className="w-5 h-5" />
                    Recent Expenses
                  </h3>
                  {selectedGroup.expenses.length > 0 ? (
                    <div className="space-y-3">
                      {selectedGroup.expenses.slice(-5).reverse().map((expense) => {
                        const paidByMember = getMembersArray(selectedGroup.members).find((m: User) => m.id === expense.paid_by);
                        return (
                          <Card key={expense.id} className="hover:shadow-md transition-shadow">
                            <CardContent className="p-4">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <div className="p-2 rounded-full bg-primary/10">
                                    <Receipt className="w-4 h-4 text-primary" />
                                  </div>
                                  <div>
                                    <p className="font-semibold">{expense.description}</p>
                                    <p className="text-sm text-muted-foreground">
                                      Paid by {paidByMember?.name || 'Unknown'} • {new Date(expense.created_at).toLocaleDateString()}
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
                            </CardContent>
                          </Card>
                        );
                      })}
                      {selectedGroup.expenses.length > 5 && (
                        <p className="text-center text-sm text-muted-foreground py-2">
                          Showing 5 most recent expenses • {selectedGroup.expenses.length - 5} more expenses in total
                        </p>
                      )}
                    </div>
                  ) : (
                    <Card className="text-center py-12 bg-muted/20">
                      <CardContent>
                        <Receipt className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                        <h4 className="font-semibold mb-2">No expenses yet</h4>
                        <p className="text-muted-foreground mb-4">
                          Start adding expenses to track group spending
                        </p>
                        <Button onClick={() => onNavigate && onNavigate("add-expense", selectedGroup.id)}>
                          <DollarSign className="w-4 h-4 mr-2" />
                          Add First Expense
                        </Button>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </div>

              {/* Action Buttons Footer */}
              <div className="border-t border-border bg-muted/20 p-6">
                <div className="flex flex-col sm:flex-row gap-3">
                  <Button 
                    onClick={() => onNavigate && onNavigate("add-expense", selectedGroup.id)}
                    className="flex-1"
                    size="lg"
                  >
                    <DollarSign className="w-4 h-4 mr-2" />
                    Add Expense
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => handleEditGroup(selectedGroup.id)}
                    className="flex-1"
                    size="lg"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Group
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      // Navigate to full expenses list for this group
                      onNavigate && onNavigate("expenses", selectedGroup.id);
                    }}
                    className="flex-1"
                    size="lg"
                  >
                    <Receipt className="w-4 h-4 mr-2" />
                    All Expenses
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirmation && groupToDelete && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowDeleteConfirmation(false);
              setGroupToDelete(null);
            }
          }}
        >
          <div className="rounded-lg shadow-lg w-full max-w-md mx-4 bg-card text-card-foreground border border-border">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <h2 className="text-lg font-semibold text-red-600">Delete Group</h2>
              <button
                onClick={() => {
                  setShowDeleteConfirmation(false);
                  setGroupToDelete(null);
                }}
                disabled={deleting}
                className="text-muted-foreground hover:text-foreground disabled:opacity-50"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="mb-4">
                <div className="flex items-center mb-3">
                  <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
                  <span className="font-medium">Are you sure?</span>
                </div>
                <p className="text-muted-foreground">
                  This will permanently delete the group <strong>"{groupToDelete.name}"</strong> and all its data. 
                  This action cannot be undone.
                </p>
              </div>

              <div className="bg-muted p-3 rounded-lg mb-4">
                <p className="text-sm text-muted-foreground">
                  <strong>Group Details:</strong>
                </p>
                <ul className="text-sm text-muted-foreground mt-1">
                  <li>• {getMembersArray(groupToDelete.members).length} members</li>
                  <li>• {groupToDelete.expenses?.length || 0} expenses</li>
                  <li>• Status: {isGroupSettled(groupToDelete) ? '✓ Settled' : '⚠ Has outstanding balances'}</li>
                </ul>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowDeleteConfirmation(false);
                    setGroupToDelete(null);
                  }}
                  disabled={deleting}
                  className="flex-1 px-4 py-2 rounded-md bg-background text-foreground border border-border hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDeleteGroup}
                  disabled={deleting}
                  className="flex-1 px-4 py-2 rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {deleting ? "Deleting..." : "Delete Group"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}