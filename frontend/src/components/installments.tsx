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
import { Progress } from "./ui/progress";
import { Input } from "./ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "./ui/tabs";
import {
  Calendar,
  Plus,
  Search,
  Filter,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  ChevronLeft,
  ChevronRight,
  Users,
  DollarSign,
} from "lucide-react";

export function Installments() {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [viewMode, setViewMode] = useState("calendar");

  const installmentPlans = [
    {
      id: 1,
      name: "Europe Trip 2025",
      description: "Summer vacation expenses",
      totalAmount: 4500.0,
      monthlyAmount: 750.0,
      startDate: "2024-10-01",
      endDate: "2025-03-01",
      group: "Travel Buddies",
      members: 3,
      status: "active",
      completedPayments: 2,
      totalPayments: 6,
      nextPayment: "2024-12-01",
      yourMonthlyShare: 250.0,
    },
    {
      id: 2,
      name: "Shared Apartment Rent",
      description: "Monthly rent split",
      totalAmount: 7200.0,
      monthlyAmount: 1200.0,
      startDate: "2024-09-01",
      endDate: "2025-02-01",
      group: "Roommates",
      members: 4,
      status: "active",
      completedPayments: 3,
      totalPayments: 6,
      nextPayment: "2025-01-01",
      yourMonthlyShare: 300.0,
    },
    {
      id: 3,
      name: "Car Purchase",
      description: "Used car for group trips",
      totalAmount: 12000.0,
      monthlyAmount: 1000.0,
      startDate: "2024-06-01",
      endDate: "2025-05-01",
      group: "Car Pool",
      members: 4,
      status: "active",
      completedPayments: 6,
      totalPayments: 12,
      nextPayment: "2025-01-01",
      yourMonthlyShare: 250.0,
    },
  ];

  const upcomingPayments = [
    {
      id: 1,
      planName: "Europe Trip 2025",
      amount: 250.0,
      dueDate: "2024-12-01",
      status: "upcoming",
      daysUntilDue: 10,
      group: "Travel Buddies",
      installmentNumber: 3,
      totalInstallments: 6,
    },
    {
      id: 2,
      planName: "Shared Apartment Rent",
      amount: 300.0,
      dueDate: "2025-01-01",
      status: "upcoming",
      daysUntilDue: 41,
      group: "Roommates",
      installmentNumber: 4,
      totalInstallments: 6,
    },
    {
      id: 3,
      planName: "Car Purchase",
      amount: 250.0,
      dueDate: "2025-01-01",
      status: "upcoming",
      daysUntilDue: 41,
      group: "Car Pool",
      installmentNumber: 7,
      totalInstallments: 12,
    },
  ];

  const monthlyBreakdown = [
    {
      month: "2024-10",
      monthName: "October 2024",
      payments: [
        {
          planName: "Europe Trip 2025",
          amount: 250.0,
          status: "paid",
          dueDate: "2024-10-01",
        },
        {
          planName: "Car Purchase",
          amount: 250.0,
          status: "paid",
          dueDate: "2024-10-01",
        },
      ],
      totalPaid: 500.0,
      totalDue: 500.0,
    },
    {
      month: "2024-11",
      monthName: "November 2024",
      payments: [
        {
          planName: "Europe Trip 2025",
          amount: 250.0,
          status: "paid",
          dueDate: "2024-11-01",
        },
        {
          planName: "Shared Apartment Rent",
          amount: 300.0,
          status: "paid",
          dueDate: "2024-11-01",
        },
        {
          planName: "Car Purchase",
          amount: 250.0,
          status: "paid",
          dueDate: "2024-11-01",
        },
      ],
      totalPaid: 800.0,
      totalDue: 800.0,
    },
    {
      month: "2024-12",
      monthName: "December 2024",
      payments: [
        {
          planName: "Europe Trip 2025",
          amount: 250.0,
          status: "upcoming",
          dueDate: "2024-12-01",
        },
        {
          planName: "Shared Apartment Rent",
          amount: 300.0,
          status: "upcoming",
          dueDate: "2024-12-01",
        },
        {
          planName: "Car Purchase",
          amount: 250.0,
          status: "upcoming",
          dueDate: "2024-12-01",
        },
      ],
      totalPaid: 0.0,
      totalDue: 800.0,
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "paid":
        return (
          <CheckCircle className="w-4 h-4 text-green-600" />
        );
      case "upcoming":
        return <Clock className="w-4 h-4 text-yellow-600" />;
      case "overdue":
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <XCircle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid":
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300";
      case "upcoming":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300";
      case "overdue":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Installments</h1>
          <p className="text-muted-foreground">
            Manage your payment plans and track monthly progress
          </p>
        </div>
        <Button className="w-full sm:w-auto gradient-primary border-0 shadow-lg">
          <Plus className="w-4 h-4 mr-2" />
          Create Installment Plan
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="gradient-card border-purple-200 dark:border-purple-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Plans
            </CardTitle>
            <Calendar className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-teal-500 bg-clip-text text-transparent">
              3
            </div>
            <p className="text-xs text-muted-foreground">
              2 ending soon
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              This Month Due
            </CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$800.00</div>
            <p className="text-xs text-muted-foreground">
              3 payments due Dec 1st
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Remaining
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">$18,200</div>
            <p className="text-xs text-muted-foreground">
              Across all active plans
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Completion Rate
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">46%</div>
            <p className="text-xs text-muted-foreground">
              11 of 24 payments made
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for different views */}
      <Tabs value={viewMode} onValueChange={setViewMode}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calendar">
            Monthly Calendar
          </TabsTrigger>
          <TabsTrigger value="plans">Active Plans</TabsTrigger>
          <TabsTrigger value="upcoming">
            Upcoming Payments
          </TabsTrigger>
        </TabsList>

        {/* Monthly Calendar View */}
        <TabsContent value="calendar" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Monthly Breakdown</CardTitle>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                  <span className="font-medium min-w-[120px] text-center">
                    {currentMonth.toLocaleDateString("en-US", {
                      month: "long",
                      year: "numeric",
                    })}
                  </span>
                  <Button variant="outline" size="sm">
                    <ChevronRight className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {monthlyBreakdown.map((month) => (
                  <Card
                    key={month.month}
                    className="border-l-4 border-l-primary"
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">
                          {month.monthName}
                        </CardTitle>
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">
                            Total Due
                          </p>
                          <p className="font-bold">
                            ${month.totalDue.toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {month.payments.map((payment, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            {getStatusIcon(payment.status)}
                            <div>
                              <p className="font-medium">
                                {payment.planName}
                              </p>
                              <p className="text-sm text-muted-foreground">
                                Due {payment.dueDate}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-bold">
                              ${payment.amount.toFixed(2)}
                            </p>
                            <Badge
                              className={`text-xs ${getStatusColor(payment.status)}`}
                            >
                              {payment.status}
                            </Badge>
                          </div>
                        </div>
                      ))}
                      <div className="flex justify-between items-center pt-2 border-t border-border">
                        <span className="font-medium">
                          Progress
                        </span>
                        <div className="flex items-center gap-2">
                          <Progress
                            value={
                              (month.totalPaid /
                                month.totalDue) *
                              100
                            }
                            className="w-20"
                          />
                          <span className="text-sm font-medium">
                            {month.totalPaid > 0
                              ? "100%"
                              : "0%"}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Active Plans View */}
        <TabsContent value="plans" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {installmentPlans.map((plan) => (
              <Card
                key={plan.id}
                className="hover:shadow-md transition-shadow"
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">
                        {plan.name}
                      </CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">
                        {plan.description}
                      </p>
                    </div>
                    <Badge
                      variant="outline"
                      className="bg-green-50 text-green-700"
                    >
                      Active
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Progress Bar */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span>
                        {plan.completedPayments}/
                        {plan.totalPayments} payments
                      </span>
                    </div>
                    <Progress
                      value={
                        (plan.completedPayments /
                          plan.totalPayments) *
                        100
                      }
                      className="h-2"
                    />
                  </div>

                  {/* Financial Details */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">
                        Total Amount
                      </p>
                      <p className="font-bold">
                        ${plan.totalAmount.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">
                        Your Monthly Share
                      </p>
                      <p className="font-bold">
                        ${plan.yourMonthlyShare.toFixed(2)}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">
                        Group
                      </p>
                      <div className="flex items-center gap-1">
                        <Users className="w-3 h-3" />
                        <span>
                          {plan.group} ({plan.members})
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-muted-foreground">
                        Next Payment
                      </p>
                      <p className="font-medium">
                        {new Date(
                          plan.nextPayment,
                        ).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                    >
                      View Details
                    </Button>
                    <Button size="sm" className="flex-1">
                      Pay Now
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Upcoming Payments View */}
        <TabsContent value="upcoming" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Payments</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {upcomingPayments.map((payment) => (
                  <div
                    key={payment.id}
                    className="flex items-center justify-between p-4 border border-border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Calendar className="w-6 h-6 text-primary" />
                      </div>
                      <div>
                        <h4 className="font-medium">
                          {payment.planName}
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {payment.group} • Installment{" "}
                          {payment.installmentNumber}/
                          {payment.totalInstallments}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Due{" "}
                          {new Date(
                            payment.dueDate,
                          ).toLocaleDateString()}{" "}
                          • {payment.daysUntilDue} days
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg">
                        ${payment.amount.toFixed(2)}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge
                          className={getStatusColor(
                            payment.status,
                          )}
                          variant="outline"
                        >
                          {payment.status}
                        </Badge>
                        <Button size="sm">Pay Now</Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}