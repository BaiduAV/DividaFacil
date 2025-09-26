import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Avatar, AvatarFallback } from "./ui/avatar";
import { Checkbox } from "./ui/checkbox";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import {
  Receipt,
  Camera,
  Users,
  DollarSign,
  Calendar,
  ArrowLeft,
  Plus,
  Minus,
  Clock,
} from "lucide-react";
import { apiClient, Group, User } from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "sonner";

interface AddExpenseProps {
  onBack: () => void;
  groupId?: string;
}

export function AddExpense({ onBack, groupId }: AddExpenseProps) {
  const { user } = useAuth();
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedPayer, setSelectedPayer] = useState("");
  const [splitType, setSplitType] = useState<"EQUAL" | "EXACT" | "PERCENTAGE">("EQUAL");
  const [isInstallment, setIsInstallment] = useState(false);
  const [installmentMonths, setInstallmentMonths] = useState("3");
  const [startDate, setStartDate] = useState("");
  const [splitAmong, setSplitAmong] = useState<string[]>([]);
  const [splitValues, setSplitValues] = useState<Record<string, number>>({});

  useEffect(() => {
    loadGroups();
    // Set default category to "other" for better UX
    if (!selectedCategory) {
      setSelectedCategory("other");
    }
  }, []);

  useEffect(() => {
    // Set initial group if groupId is provided
    if (groupId && groups.length > 0) {
      const group = groups.find(g => g.id === groupId);
      if (group) {
        setSelectedGroup(groupId);
      }
    }
  }, [groupId, groups]);

  useEffect(() => {
    // Set default payer to current user
    if (user && !selectedPayer) {
      setSelectedPayer(user.id);
    }
  }, [user, selectedPayer]);

  useEffect(() => {
    // When group changes, update split among to include all group members
    if (selectedGroup && groups.length > 0) {
      const group = groups.find(g => g.id === selectedGroup);
      if (group) {
        const memberIds = Object.keys(group.members);
        setSplitAmong(memberIds);
        // Reset split values when group changes
        setSplitValues({});
      }
    }
  }, [selectedGroup, groups]);

  const loadGroups = async () => {
    try {
      setLoading(true);
      const userGroups = await apiClient.getGroups();
      setGroups(userGroups);
    } catch (error) {
      toast.error("Failed to load groups");
      console.error("Load groups error:", error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: "food", name: "Food & Drink", icon: "🍽️" },
    { id: "transport", name: "Transportation", icon: "🚗" },
    { id: "accommodation", name: "Accommodation", icon: "🏨" },
    { id: "entertainment", name: "Entertainment", icon: "🎬" },
    { id: "shopping", name: "Shopping", icon: "🛍️" },
    { id: "other", name: "Other", icon: "💰" },
  ];

  // Get current group members
  const currentGroup = groups.find(g => g.id === selectedGroup);
  const groupMembers = currentGroup ? Object.values(currentGroup.members).map(member => ({
    id: member.id,
    name: member.name,
    initials: member.name.split(' ').map(n => n[0]).join('').toUpperCase(),
    isYou: user?.id === member.id
  })) : [];

  const [selectedMembers, setSelectedMembers] = useState<string[]>([]);

  useEffect(() => {
    // Update selected members when group changes
    setSelectedMembers(groupMembers.map(member => member.id));
  }, [selectedGroup, groups]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedGroup || !description || !amount || !selectedPayer) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (!selectedCategory) {
      toast.error("Please select a category for the expense");
      return;
    }

    if (selectedMembers.length === 0) {
      toast.error("Please select at least one member to split with");
      return;
    }

    try {
      setSubmitting(true);
      
      const expenseData = {
        description,
        amount: parseFloat(amount),
        paid_by: selectedPayer,
        category: selectedCategory, // Category is now always set (default or selected)
        split_type: splitType,
        split_among: selectedMembers,
        split_values: splitType === "EQUAL" 
          ? {} 
          : selectedMembers.reduce((acc, memberId) => {
              acc[memberId] = splitValues[memberId] || 0;
              return acc;
            }, {} as Record<string, number>),
        installments_count: isInstallment ? parseInt(installmentMonths) : 1,
        first_due_date: startDate ? new Date(startDate).toISOString() : undefined,
      };

      await apiClient.createExpense(selectedGroup, expenseData);
      toast.success("Expense added successfully!");
      onBack();
    } catch (error) {
      toast.error("Failed to add expense");
      console.error("Add expense error:", error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleMemberToggle = (memberId: string) => {
    setSelectedMembers((prev) =>
      prev.includes(memberId)
        ? prev.filter((id) => id !== memberId)
        : [...prev, memberId],
    );
  };

  const calculateSplit = () => {
    if (!amount || selectedMembers.length === 0) return "0.00";
    const totalPerPerson =
      parseFloat(amount) / selectedMembers.length;
    if (isInstallment) {
      return (
        totalPerPerson / parseInt(installmentMonths)
      ).toFixed(2);
    }
    return totalPerPerson.toFixed(2);
  };

  const calculateMonthlyTotal = () => {
    if (!amount || !isInstallment) return 0;
    return (
      parseFloat(amount) / parseInt(installmentMonths)
    ).toFixed(2);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button type="button" variant="ghost" size="sm" onClick={onBack}>
          <ArrowLeft className="w-4 h-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Add Expense</h1>
          <p className="text-muted-foreground">
            Split a new expense with friends
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Receipt className="w-5 h-5" />
                Expense Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount</Label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      id="amount"
                      type="number"
                      placeholder="0.00"
                      value={amount}
                      onChange={(e) =>
                        setAmount(e.target.value)
                      }
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select
                    value={selectedCategory}
                    onValueChange={setSelectedCategory}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem
                          key={category.id}
                          value={category.id}
                        >
                          <div className="flex items-center gap-2">
                            <span>{category.icon}</span>
                            {category.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  placeholder="What was this expense for?"
                  value={description}
                  onChange={(e) =>
                    setDescription(e.target.value)
                  }
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="group">Group</Label>
                <Select
                  value={selectedGroup}
                  onValueChange={setSelectedGroup}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a group" />
                  </SelectTrigger>
                  <SelectContent>
                    {groups.map((group) => (
                      <SelectItem
                        key={group.id}
                        value={group.id}
                      >
                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4" />
                          {group.name} ({Object.keys(group.members).length} members)
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Installment Toggle */}
              <div className="flex items-center justify-between p-4 border border-border rounded-lg">
                <div className="flex items-center gap-3">
                  <Clock className="w-5 h-5 text-primary" />
                  <div>
                    <Label
                      htmlFor="installment-toggle"
                      className="font-medium"
                    >
                      Create Installment Plan
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Split this expense into monthly payments
                    </p>
                  </div>
                </div>
                <Switch
                  id="installment-toggle"
                  checked={isInstallment}
                  onCheckedChange={setIsInstallment}
                />
              </div>
            </CardContent>
          </Card>

          {/* Installment Details */}
          {isInstallment && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  Installment Plan Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="installment-months">
                      Number of Months
                    </Label>
                    <Select
                      value={installmentMonths}
                      onValueChange={setInstallmentMonths}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select duration" />
                      </SelectTrigger>
                      <SelectContent>
                        {[3, 6, 12, 18, 24].map((months) => (
                          <SelectItem
                            key={months}
                            value={months.toString()}
                          >
                            {months} months
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="start-date">
                      Start Date
                    </Label>
                    <Input
                      id="start-date"
                      type="month"
                      value={startDate}
                      onChange={(e) =>
                        setStartDate(e.target.value)
                      }
                    />
                  </div>
                </div>

                <div className="p-4 bg-muted/50 rounded-lg">
                  <h4 className="font-medium mb-2">
                    Payment Schedule Preview
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Monthly Amount (Total):</span>
                      <span className="font-medium">
                        ${calculateMonthlyTotal()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Your Monthly Share:</span>
                      <span className="font-medium">
                        ${calculateSplit()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Duration:</span>
                      <span className="font-medium">
                        {installmentMonths} months
                      </span>
                    </div>
                    {startDate && (
                      <div className="flex justify-between">
                        <span>Final Payment:</span>
                        <span className="font-medium">
                          {new Date(
                            new Date(startDate).setMonth(
                              new Date(startDate).getMonth() +
                                parseInt(installmentMonths) -
                                1,
                            ),
                          ).toLocaleDateString("en-US", {
                            month: "short",
                            year: "numeric",
                          })}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Who Paid */}
          <Card>
            <CardHeader>
              <CardTitle>Who Paid?</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {groupMembers.map((member) => (
                  <Button
                    key={member.id}
                    variant={
                      selectedPayer === member.id
                        ? "default"
                        : "outline"
                    }
                    className="h-auto p-3 flex flex-col gap-2"
                    onClick={() => setSelectedPayer(member.id)}
                  >
                    <Avatar className="w-8 h-8">
                      <AvatarFallback className="text-xs">
                        {member.initials}
                      </AvatarFallback>
                    </Avatar>
                    <span className="text-sm">
                      {member.isYou ? "You" : member.name}
                    </span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Split Details */}
          <Card>
            <CardHeader>
              <CardTitle>How to Split?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <Button
                  variant={
                    splitType === "EQUAL"
                      ? "default"
                      : "outline"
                  }
                  onClick={() => setSplitType("EQUAL")}
                  className="h-auto p-3 flex flex-col gap-1"
                >
                  <div className="text-sm font-medium">
                    Equal Split
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Split equally among all
                  </div>
                </Button>
                <Button
                  variant={
                    splitType === "EXACT"
                      ? "default"
                      : "outline"
                  }
                  onClick={() => setSplitType("EXACT")}
                  className="h-auto p-3 flex flex-col gap-1"
                >
                  <div className="text-sm font-medium">
                    Exact Amounts
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Specify exact amounts
                  </div>
                </Button>
                <Button
                  variant={
                    splitType === "PERCENTAGE"
                      ? "default"
                      : "outline"
                  }
                  onClick={() => setSplitType("PERCENTAGE")}
                  className="h-auto p-3 flex flex-col gap-1"
                >
                  <div className="text-sm font-medium">
                    Percentages
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Split by percentages
                  </div>
                </Button>
              </div>

              {/* Member Selection */}
              <div className="space-y-3">
                <Label>Who's involved?</Label>
                <div className="space-y-2">
                  {groupMembers.map((member) => (
                    <div
                      key={member.id}
                      className="flex items-center justify-between p-3 border border-border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <Checkbox
                          checked={selectedMembers.includes(
                            member.id,
                          )}
                          onCheckedChange={() =>
                            handleMemberToggle(member.id)
                          }
                        />
                        <Avatar className="w-8 h-8">
                          <AvatarFallback className="text-xs">
                            {member.initials}
                          </AvatarFallback>
                        </Avatar>
                        <span className="font-medium">
                          {member.isYou ? "You" : member.name}
                        </span>
                      </div>
                      {selectedMembers.includes(member.id) &&
                        splitType === "EQUAL" && (
                          <Badge variant="secondary">
                            ${calculateSplit()}
                            {isInstallment ? "/month" : ""}
                          </Badge>
                        )}
                      {selectedMembers.includes(member.id) &&
                        splitType === "EXACT" && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm">$</span>
                            <Input
                              type="number"
                              placeholder="0.00"
                              value={splitValues[member.id] || ""}
                              onChange={(e) => {
                                const value = parseFloat(e.target.value) || 0;
                                setSplitValues(prev => ({
                                  ...prev,
                                  [member.id]: value
                                }));
                              }}
                              className="w-20 h-8"
                            />
                          </div>
                        )}
                      {selectedMembers.includes(member.id) &&
                        splitType === "PERCENTAGE" && (
                          <div className="flex items-center gap-2">
                            <Input
                              type="number"
                              placeholder="0"
                              value={splitValues[member.id] || ""}
                              onChange={(e) => {
                                const value = parseFloat(e.target.value) || 0;
                                setSplitValues(prev => ({
                                  ...prev,
                                  [member.id]: value
                                }));
                              }}
                              className="w-16 h-8"
                            />
                            <span className="text-sm">%</span>
                          </div>
                        )}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Summary Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Total Amount:
                  </span>
                  <span className="font-medium">
                    ${amount || "0.00"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    Split Between:
                  </span>
                  <span className="font-medium">
                    {selectedMembers.length} people
                  </span>
                </div>
                {isInstallment && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">
                        Duration:
                      </span>
                      <span className="font-medium">
                        {installmentMonths} months
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">
                        Monthly Total:
                      </span>
                      <span className="font-medium">
                        ${calculateMonthlyTotal()}
                      </span>
                    </div>
                  </>
                )}
                <div className="flex justify-between">
                  <span className="text-muted-foreground">
                    {isInstallment
                      ? "Your Monthly Share:"
                      : "Per Person:"}
                  </span>
                  <span className="font-medium">
                    ${calculateSplit()}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-border space-y-2">
                <div className="text-sm font-medium">
                  {isInstallment
                    ? "Payment Plan:"
                    : "You will:"}
                </div>
                {isInstallment ? (
                  <div className="text-sm text-muted-foreground">
                    {selectedPayer === user?.id
                      ? `Pay ${installmentMonths} monthly installments of ${calculateSplit()}`
                      : `Owe ${installmentMonths} monthly payments of ${calculateSplit()} to ${groupMembers.find((m) => m.id === selectedPayer)?.name}`}
                  </div>
                ) : selectedPayer === user?.id ? (
                  <div className="text-sm text-muted-foreground">
                    Pay ${amount || "0.00"} and get back $
                    {(
                      parseFloat(amount || "0") -
                      parseFloat(calculateSplit())
                    ).toFixed(2)}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">
                    Owe ${calculateSplit()} to{" "}
                    {
                      groupMembers.find(
                        (m) => m.id === selectedPayer,
                      )?.name
                    }
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <Button className="w-full mb-3">
                <Camera className="w-4 h-4 mr-2" />
                Scan Receipt
              </Button>
              <Button variant="outline" className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add Another Expense
              </Button>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={onBack}
            >
              Cancel
            </Button>
            <Button className="flex-1 gradient-primary border-0 shadow-lg" type="submit" disabled={submitting}>
              {submitting ? (
                "Adding..."
              ) : isInstallment ? (
                "Create Installment Plan"
              ) : (
                "Add Expense"
              )}
            </Button>
          </div>
        </div>
      </div>
    </form>
  );
}