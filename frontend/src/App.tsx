import { useState } from "react";
import { Navigation } from "./components/navigation";
import { Dashboard } from "./components/dashboard";
import { Groups } from "./components/groups";
import { GroupDetails } from "./components/group-details";
import { Expenses } from "./components/expenses";
import { Installments } from "./components/installments";
import { AddExpense } from "./components/add-expense";
import { Login } from "./components/login";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner";
import { useAuth } from "./contexts/AuthContext";
import { apiClient } from "./services/api";

export default function App() {
  const { user, isLoading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [openCreateGroupModal, setOpenCreateGroupModal] = useState(false);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [refreshGroups, setRefreshGroups] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState<any>(null);

  const handleNavigateToGroups = (tab: string, openModal = false) => {
    setActiveTab(tab);
    if (tab === "groups" && openModal) {
      setOpenCreateGroupModal(true);
    }
  };

  const handleNavigate = (tab: string, groupId?: string) => {
    setActiveTab(tab);
    if (groupId) {
      setSelectedGroupId(groupId);
      // Fetch group details when navigating to group-details
      if (tab === "group-details") {
        fetchGroupDetails(groupId);
      }
    }
    // Trigger groups refresh when navigating to groups tab
    if (tab === "groups") {
      setRefreshGroups(prev => !prev);
    }
  };

  const fetchGroupDetails = async (groupId: string) => {
    try {
      const groups = await apiClient.getGroups();
      const group = groups.find(g => g.id === groupId);
      setSelectedGroup(group);
    } catch (error) {
      console.error("Failed to fetch group details:", error);
    }
  };

  const handleDeleteGroup = async (groupId: string) => {
    if (!selectedGroup) {
      toast.error("No group selected for deletion");
      return;
    }
    
    try {
      await apiClient.deleteGroup(groupId);
      toast.success(`Group "${selectedGroup.name}" deleted successfully!`);
      
      // Navigate back to groups and refresh
      setActiveTab("groups");
      setRefreshGroups(prev => !prev);
      setSelectedGroup(null);
    } catch (error: any) {
      console.error("Failed to delete group:", error);
      if (error.status === 400) {
        toast.error("Cannot delete group with outstanding balances. Please settle all debts first.");
      } else if (error.status === 403) {
        toast.error("You don't have permission to delete this group.");
      } else if (error.status === 404) {
        toast.error("Group not found.");
      } else {
        toast.error("Failed to delete group. Please try again.");
      }
    }
  };

  const handleEditGroup = (groupId: string) => {
    // TODO: Implement edit group functionality
    console.log("Edit group", groupId);
    toast.info("Edit group functionality coming soon!");
  };

  const handleAddMembers = (groupId: string) => {
    // TODO: Implement add members functionality
    console.log("Add members", groupId);
    toast.info("Add members functionality coming soon!");
  };

  const handleExpenseAdded = () => {
    // Navigate back to groups and trigger refresh
    setActiveTab("groups");
    setRefreshGroups(prev => !prev);
  };

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard onNavigate={handleNavigateToGroups} />;
      case "groups":
        return (
          <Groups 
            openCreateModal={openCreateGroupModal}
            onCreateModalClose={() => setOpenCreateGroupModal(false)}
            onNavigate={handleNavigate}
            refreshTrigger={refreshGroups}
          />
        );
      case "group-details":
        return selectedGroup && user ? (
          <GroupDetails
            group={selectedGroup}
            currentUser={user}
            onBack={() => setActiveTab("groups")}
            onNavigate={handleNavigate}
            onEditGroup={handleEditGroup}
            onAddMembers={handleAddMembers}
            onDeleteGroup={handleDeleteGroup}
          />
        ) : (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-4">Loading...</h2>
            <p className="text-muted-foreground">Loading group details...</p>
          </div>
        );
      case "expenses":
        return <Expenses />;
      case "installments":
        return <Installments />;
      case "add-expense":
        return (
          <AddExpense
            onBack={handleExpenseAdded}
            groupId={selectedGroupId || undefined}
          />
        );
      case "reports":
        return (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-4">Reports</h2>
            <p className="text-muted-foreground">
              Expense reports and analytics coming soon...
            </p>
          </div>
        );
      case "settings":
        return (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-4">
              Settings
            </h2>
            <p className="text-muted-foreground">
              App settings and preferences coming soon...
            </p>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Carregando...</p>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!user) {
    return (
      <>
        <Login />
        <Toaster />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() =>
          setIsSidebarCollapsed(!isSidebarCollapsed)
        }
        user={user}
        onLogout={logout}
      />

      {/* Main Content */}
      <main
        className={`pt-16 pb-16 lg:pt-0 lg:pb-0 transition-all duration-300 ${isSidebarCollapsed ? "lg:pl-16" : "lg:pl-64"}`}
      >
        <div className="container mx-auto px-4 py-6 lg:py-8">
          {renderContent()}
        </div>
      </main>
      
      <Toaster />
    </div>
  );
}