import { useState } from "react";
import { Navigation } from "./components/navigation";
import { Dashboard } from "./components/dashboard";
import { Groups } from "./components/groups";
import { Expenses } from "./components/expenses";
import { Installments } from "./components/installments";
import { AddExpense } from "./components/add-expense";
import { Login } from "./components/login";
import { Toaster } from "./components/ui/sonner";
import { useAuth } from "./contexts/AuthContext";

export default function App() {
  const { user, isLoading, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [openCreateGroupModal, setOpenCreateGroupModal] = useState(false);
  const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
  const [refreshGroups, setRefreshGroups] = useState(false);

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
    }
    // Trigger groups refresh when navigating to groups tab
    if (tab === "groups") {
      setRefreshGroups(prev => !prev);
    }
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