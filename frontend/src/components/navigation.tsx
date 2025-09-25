import { useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
  SheetDescription,
} from "./ui/sheet";
import { Button } from "./ui/button";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Badge } from "./ui/badge";
import { ThemeToggle } from "./theme-toggle";
import {
  Menu,
  Home,
  Users,
  Receipt,
  PieChart,
  Settings,
  Plus,
  Bell,
  Calendar,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";

interface User {
  email: string;
  name: string;
}

interface NavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  user?: User | null;
  onLogout?: () => void;
}

export function Navigation({
  activeTab,
  onTabChange,
  isCollapsed = false,
  onToggleCollapse,
  user,
  onLogout,
}: NavigationProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
  };

  const navigationItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "groups", label: "Groups", icon: Users },
    { id: "expenses", label: "Expenses", icon: Receipt },
    {
      id: "installments",
      label: "Installments",
      icon: Calendar,
    },
    { id: "reports", label: "Reports", icon: PieChart },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const NavContent = ({ forMobile = false }) => (
    <TooltipProvider>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div
          className={`border-b border-border ${isCollapsed && !forMobile ? "p-4 pb-6" : "p-6"}`}
        >
          <div
            className={`flex items-center ${isCollapsed && !forMobile ? "justify-start" : "gap-3"}`}
          >
            {isCollapsed && !forMobile ? (
              // Collapsed header - centered app icon
              <div className="flex justify-center">
                <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center shadow-lg flex-shrink-0">
                  <Receipt className="w-4 h-4 text-white" />
                </div>
              </div>
            ) : (
              // Expanded header - normal layout with app branding
              <>
                <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center shadow-lg flex-shrink-0">
                  <Receipt className="w-4 h-4 text-white" />
                </div>
                <div className="flex-1">
                  <h2 className="font-medium bg-gradient-to-r from-purple-600 to-teal-500 bg-clip-text text-transparent">
                    DividaFacil
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Expense Tracker
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const NavButton = (
                <Button
                  key={item.id}
                  variant={
                    activeTab === item.id
                      ? "secondary"
                      : "ghost"
                  }
                  className={`w-full h-11 ${isCollapsed && !forMobile ? "justify-center px-0" : "justify-start gap-3"}`}
                  onClick={() => {
                    onTabChange(item.id);
                    setIsOpen(false);
                  }}
                >
                  <Icon className="w-4 h-4" />
                  {(!isCollapsed || forMobile) && item.label}
                </Button>
              );

              if (isCollapsed && !forMobile) {
                return (
                  <Tooltip key={item.id}>
                    <TooltipTrigger asChild>
                      {NavButton}
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      <p>{item.label}</p>
                    </TooltipContent>
                  </Tooltip>
                );
              }

              return NavButton;
            })}
          </div>
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-border">
          {isCollapsed && !forMobile ? (
            // Collapsed user profile
            <div className="space-y-3">
              <div className="flex justify-center">
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Avatar className="w-8 h-8 cursor-pointer">
                      <AvatarFallback className="text-xs">
                        {user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'}
                      </AvatarFallback>
                    </Avatar>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <div>
                      <p className="font-medium">{user?.name || 'User'}</p>
                      <p className="text-xs text-muted-foreground">
                        {user?.email || 'user@example.com'}
                      </p>
                    </div>
                  </TooltipContent>
                </Tooltip>
              </div>
              <div className="flex flex-col items-center gap-2">
                <ThemeToggle />
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                      onClick={handleLogout}
                    >
                      <LogOut className="w-4 h-4" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="right">
                    <p>Logout</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>
          ) : (
            // Expanded user profile
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="text-xs">
                    {user?.name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {user?.email || 'user@example.com'}
                  </p>
                </div>
              </div>
              <div className="flex items-center justify-between px-3">
                <ThemeToggle />
                <Button
                  variant="ghost"
                  size="sm"
                  className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                  onClick={handleLogout}
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="ml-1.5 text-xs">Logout</span>
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </TooltipProvider>
  );

  return (
    <>
      {/* Mobile Navigation */}
      <div className="lg:hidden">
        {/* Top Bar */}
        <div className="fixed top-0 left-0 right-0 z-40 h-16 bg-background border-b border-border flex items-center justify-between px-4">
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="p-2">
                <Menu className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-80">
              <SheetTitle className="sr-only">
                Navigation Menu
              </SheetTitle>
              <SheetDescription className="sr-only">
                Main navigation menu for the expense splitter
                app
              </SheetDescription>
              <NavContent forMobile={true} />
            </SheetContent>
          </Sheet>

          <div className="flex items-center gap-2">
            <div className="w-6 h-6 gradient-primary rounded flex items-center justify-center shadow-lg">
              <Receipt className="w-3 h-3 text-white" />
            </div>
            <span className="font-medium bg-gradient-to-r from-purple-600 to-teal-500 bg-clip-text text-transparent">
              DividaFacil
            </span>
          </div>

          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button
              variant="ghost"
              size="sm"
              className="p-2 relative"
            >
              <Bell className="w-5 h-5" />
              <Badge className="absolute -top-1 -right-1 w-4 h-4 p-0 text-xs bg-destructive text-destructive-foreground">
                3
              </Badge>
            </Button>
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="fixed bottom-0 left-0 right-0 z-40 h-16 bg-background border-t border-border">
          <div className="flex items-center h-full">
            {navigationItems.slice(0, 5).map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={`flex-1 flex flex-col items-center justify-center gap-1 h-full transition-colors ${
                    activeTab === item.id
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  onClick={() => onTabChange(item.id)}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs">{item.label}</span>
                </button>
              );
            })}
            <div className="flex-1 flex items-center justify-center">
              <Button
                size="sm"
                className="w-10 h-10 rounded-full p-0"
                onClick={() => onTabChange("add-expense")}
              >
                <Plus className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Desktop Navigation */}
      <div
        className={`hidden lg:block fixed left-0 top-0 bottom-0 bg-background border-r border-border z-30 transition-all duration-300 ${isCollapsed ? "w-16" : "w-64"}`}
      >
        <NavContent />
      </div>

      {/* Floating Toggle Arrow - Desktop Only */}
      {onToggleCollapse && (
        <div className="hidden lg:block">
          <div 
            className={`fixed top-6 z-50 transition-all duration-300 ${isCollapsed ? "left-16" : "left-64"}`}
            style={{ transform: 'translateX(-50%)' }}
          >
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-8 h-8 rounded-full p-0 bg-background hover:bg-accent shadow-lg border-2 transition-all duration-200 hover:scale-110"
                    onClick={onToggleCollapse}
                  >
                    {isCollapsed ? (
                      <ChevronRight className="w-4 h-4" />
                    ) : (
                      <ChevronLeft className="w-4 h-4" />
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="right" className="ml-2">
                  <p>{isCollapsed ? "Expand sidebar" : "Collapse sidebar"}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>
      )}
    </>
  );
}