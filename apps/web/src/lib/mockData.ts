export interface ShadowAlert {
  id: string;
  department: string;
  processName: string;
  riskScore: number; // 0-100
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  estimatedLeakage: string;
  unapprovedTool: string;
  detectedAt: string;
  status: 'Investigating' | 'Flagged' | 'Resolved';
}

export interface InvoiceItem {
  id: string;
  vendorName: string;
  gstin: string;
  invoiceNumber: string;
  amount: number;
  gstAmount: number;
  isArithmeticValid: boolean;
  isDuplicate: boolean;
  date: string;
  status: 'Verified' | 'Action Required' | 'Duplicate Alert';
  pdfUrl?: string;
  items: { description: string; qty: number; unitPrice: number; total: number }[];
}

export interface DemandItem {
  id: string;
  requestedBy: string;
  department: string;
  category: string;
  itemName: string;
  estCost: string;
  aiRecommendation: string;
  approvalStatus: 'Pending Manager' | 'Pending Finance' | 'Approved' | 'Rejected';
  matchedAssetAvailable: boolean;
  suggestedAction: string;
}

export interface PhysicalAsset {
  id: string;
  assetTag: string;
  name: string;
  category: string;
  location: string;
  assignedUser: string;
  status: 'Active' | 'Dormant (Reallocatable)' | 'Maintenance Required';
  telemetry: {
    batteryPct: number;
    tempCelsius: number;
    lastPing: string;
    signalStrength: string;
  };
}

export interface AuditLog {
  id: string;
  timestamp: string;
  actor: string;
  role: string;
  action: string;
  target: string;
  confidenceScore?: number;
}

export const mockShadowScore = 74; // composite score

export const mockShadowAlerts: ShadowAlert[] = [
  {
    id: 'SHD-9021',
    department: 'Marketing & Growth',
    processName: 'Unsanctioned Cloud Analytics Subscription',
    riskScore: 88,
    severity: 'Critical',
    estimatedLeakage: '$14,200 / yr',
    unapprovedTool: 'Mixpanel (Personal Credit Card Claim)',
    detectedAt: '12 mins ago',
    status: 'Flagged',
  },
  {
    id: 'SHD-9022',
    department: 'Engineering',
    processName: 'Bypassed Security Gateway for External API',
    riskScore: 76,
    severity: 'High',
    estimatedLeakage: '$8,500 / mo',
    unapprovedTool: 'Unverified LLM Proxy Service',
    detectedAt: '45 mins ago',
    status: 'Investigating',
  },
  {
    id: 'SHD-9023',
    department: 'Operations',
    processName: 'Duplicate Freight Forwarder Vendor Creation',
    riskScore: 64,
    severity: 'Medium',
    estimatedLeakage: '$22,000 one-time',
    unapprovedTool: 'Direct Vendor Invoice Submission',
    detectedAt: '3 hours ago',
    status: 'Flagged',
  },
  {
    id: 'SHD-9024',
    department: 'Product Design',
    processName: 'Personal Figma Team Account Expensing',
    riskScore: 42,
    severity: 'Low',
    estimatedLeakage: '$1,800 / yr',
    unapprovedTool: 'Figma Organization Bypass',
    detectedAt: 'Yesterday',
    status: 'Resolved',
  },
];

export const mockInvoices: InvoiceItem[] = [
  {
    id: 'INV-2026-081',
    vendorName: 'Apex Cloud Solutions Private Limited',
    gstin: '27AAACA12341Z5',
    invoiceNumber: 'APX-99412',
    amount: 118000,
    gstAmount: 18000,
    isArithmeticValid: true,
    isDuplicate: false,
    date: '2026-09-20',
    status: 'Verified',
    items: [
      { description: 'Dedicated Enterprise Cloud Node (Sep 2026)', qty: 1, unitPrice: 100000, total: 100000 },
      { description: 'GST @ 18%', qty: 1, unitPrice: 18000, total: 18000 },
    ],
  },
  {
    id: 'INV-2026-082',
    vendorName: 'Global Logistics Hub Ltd',
    gstin: '07BBBCC56781Z9',
    invoiceNumber: 'GLH-88419',
    amount: 54000,
    gstAmount: 9000, // Invalid arithmetic: 18% of 45000 is 8100, but invoice says 9000
    isArithmeticValid: false,
    isDuplicate: false,
    date: '2026-09-21',
    status: 'Action Required',
    items: [
      { description: 'Inter-state Asset Freight Charges', qty: 1, unitPrice: 45000, total: 45000 },
      { description: 'Incorrect Tax Math (Claimed 20%)', qty: 1, unitPrice: 9000, total: 9000 },
    ],
  },
  {
    id: 'INV-2026-083',
    vendorName: 'Apex Cloud Solutions Private Limited',
    gstin: '27AAACA12341Z5',
    invoiceNumber: 'APX-99412', // Duplicate invoice number!
    amount: 118000,
    gstAmount: 18000,
    isArithmeticValid: true,
    isDuplicate: true,
    date: '2026-09-22',
    status: 'Duplicate Alert',
    items: [
      { description: 'Duplicate Claim for Dedicated Cloud Node', qty: 1, unitPrice: 100000, total: 100000 },
    ],
  },
];

export const mockDemands: DemandItem[] = [
  {
    id: 'DEM-401',
    requestedBy: 'Sarah Jenkins',
    department: 'Data Science',
    category: 'Hardware Workstation',
    itemName: 'MacBook Pro M4 Max (64GB RAM)',
    estCost: '$3,800',
    aiRecommendation: 'Dormant asset match found! 1 unused M3 Max laptop available in IT inventory.',
    approvalStatus: 'Pending Finance',
    matchedAssetAvailable: true,
    suggestedAction: 'Reallocate Inventory Asset #AST-8821 instead of purchasing.',
  },
  {
    id: 'DEM-402',
    requestedBy: 'Daniel Rivera',
    department: 'Product',
    category: 'Software License',
    itemName: 'Notion Enterprise Workspace Seats (x15)',
    estCost: '$4,500 / yr',
    aiRecommendation: 'Policy compliant. Consolidated vendor discount pre-negotiated at 15%.',
    approvalStatus: 'Pending Manager',
    matchedAssetAvailable: false,
    suggestedAction: 'Approve with pre-negotiated Master Service Agreement #MSA-2025.',
  },
];

export const mockAssets: PhysicalAsset[] = [
  {
    id: 'AST-8821',
    assetTag: 'ORG-HW-08821',
    name: 'Apple MacBook Pro M3 Max 16"',
    category: 'Laptops',
    location: 'Building B - IT Depot Locker 4',
    assignedUser: 'Unassigned (Dormant > 45 days)',
    status: 'Dormant (Reallocatable)',
    telemetry: {
      batteryPct: 94,
      tempCelsius: 22,
      lastPing: '2 mins ago',
      signalStrength: 'Excellent',
    },
  },
  {
    id: 'AST-8822',
    assetTag: 'ORG-HW-08822',
    name: 'Dell UltraSharp 38" Curved Monitor',
    category: 'Displays',
    location: 'Building A - Desk 402',
    assignedUser: 'Sarah Rivera',
    status: 'Active',
    telemetry: {
      batteryPct: 100,
      tempCelsius: 34,
      lastPing: '10 secs ago',
      signalStrength: 'Strong',
    },
  },
  {
    id: 'AST-8823',
    assetTag: 'ORG-HW-08823',
    name: 'Cisco Meraki Access Point GX-50',
    category: 'Networking IoT',
    location: 'Building C - Floor 2 Server Closet',
    assignedUser: 'Infrastructure Team',
    status: 'Active',
    telemetry: {
      batteryPct: 100,
      tempCelsius: 41,
      lastPing: 'Just now',
      signalStrength: 'Strong',
    },
  },
];

export const mockAuditLogs: AuditLog[] = [
  {
    id: 'AUD-1001',
    timestamp: '11:45:02',
    actor: 'System AI Engine v2.4',
    role: 'Automated Governance',
    action: 'Flagged Duplicate Invoice',
    target: 'INV-2026-083 (Apex Cloud)',
    confidenceScore: 0.99,
  },
  {
    id: 'AUD-1002',
    timestamp: '11:32:18',
    actor: 'Sarah Livera',
    role: 'Procurement Admin',
    action: 'Approved Reallocation Request',
    target: 'DEM-401 -> AST-8821',
  },
  {
    id: 'AUD-1003',
    timestamp: '10:14:55',
    actor: 'GSTIN Validation API',
    role: 'Compliance Service',
    action: 'Verified Vendor GSTIN',
    target: '27AAACA12341Z5',
    confidenceScore: 1.0,
  },
];

export const mockCollaborators = [
  { name: 'Sarah Livera', role: 'Procurement Lead', avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces', status: 'online' },
  { name: 'Daniel Clark', role: 'Finance Director', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces', status: 'online' },
  { name: 'Andy Rivers', role: 'IT Manager', avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=faces', status: 'away' },
];
