import { useState } from "react";
import { Navigation } from "./components/navigation";
import { Dashboard } from "./components/dashboard";
import { Groups } from "./components/groups";
import { Expenses } from "./components/expenses";
import { Installments } from "./components/installments";
import { AddExpense } from "./components/add-expense";
import { Login } from "./components/login";
import { Toaster } from "./components/ui/sonner";

interface User {
  email: string;
  name: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = (userData: User) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    setActiveTab("dashboard"); // Reset to dashboard on logout
  };

  const renderContent = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "groups":
        return <Groups />;
      case "expenses":
        return <Expenses />;
      case "installments":
        return <Installments />;
      case "add-expense":
        return (
          <AddExpense
            onBack={() => setActiveTab("dashboard")}
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

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return (
      <>
        <Login onLogin={handleLogin} />
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
        onLogout={handleLogout}
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