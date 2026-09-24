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
  brand?: string;
  category: string;
  location: string;
  assignedUser: string;
  status: 'Active' | 'Dormant (Reallocatable)' | 'Maintenance Required';
  priceInr?: number;
  benchmarkScore?: number;
  processor?: string;
  cores?: string;
  ram?: string;
  ramType?: string;
  storage?: string;
  telemetry: {
    batteryPct: number;
    tempCelsius: number;
    lastPing: string;
    signalStrength: string;
  };
}

export interface LaptopDatasetItem {
  id: string;
  brand: string;
  model: string;
  priceInr: number;
  benchmarkScore: number;
  processor: string;
  cores: string;
  ram: string;
  ramType: string;
  storage: string;
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
    gstAmount: 9000,
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
    invoiceNumber: 'APX-99412',
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

// Exact Dataset provided by user
export const laptopHardwareDataset: LaptopDatasetItem[] = [
  {
    id: 'LPT-001',
    brand: 'HP',
    model: 'Victus 15-fb0157AX Gaming Laptop',
    priceInr: 49900,
    benchmarkScore: 73.0,
    processor: '5th Gen AMD Ryzen 5 5600H',
    cores: 'Hexa Core, 12 Threads',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '512GB',
  },
  {
    id: 'LPT-002',
    brand: 'HP',
    model: '15s-fq5007TU Laptop',
    priceInr: 39900,
    benchmarkScore: 60.0,
    processor: '12th Gen Intel Core i3 1215U',
    cores: 'Hexa Core (2P + 4E), 8 Threads',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '512GB',
  },
  {
    id: 'LPT-003',
    brand: 'Acer',
    model: 'One 14 Z8-415 Laptop',
    priceInr: 26990,
    benchmarkScore: 69.323529,
    processor: '11th Gen Intel Core i3 1115G4',
    cores: 'Dual Core, 4 Threads',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '512GB',
  },
  {
    id: 'LPT-004',
    brand: 'Lenovo',
    model: 'Yoga Slim 6 14IAP8 82WU0095IN Laptop',
    priceInr: 59729,
    benchmarkScore: 66.0,
    processor: '12th Gen Intel Core i5 1240P',
    cores: '12 Cores (4P + 8E), 16 Threads',
    ram: '16GB',
    ramType: 'LPDDR5',
    storage: '512GB',
  },
  {
    id: 'LPT-005',
    brand: 'Apple',
    model: 'MacBook Air 2020 MGND3HN Laptop',
    priceInr: 69990,
    benchmarkScore: 69.323529,
    processor: 'Apple M1',
    cores: 'Octa Core (4P + 4E)',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '256GB',
  },
  {
    id: 'LPT-006',
    brand: 'Asus',
    model: 'Vivobook 15X 2023 K3504VAB-NJ321WS Laptop',
    priceInr: 44990,
    benchmarkScore: 69.323529,
    processor: '13th Gen Intel Core i3 1315U',
    cores: 'Hexa Core (2P + 4E), 8 Threads',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '512GB',
  },
  {
    id: 'LPT-007',
    brand: 'Asus',
    model: 'TUF A15 FA577RM-HQ032WS Laptop',
    priceInr: 110000,
    benchmarkScore: 71.0,
    processor: '6th Gen AMD Ryzen 7 6800H',
    cores: 'Octa Core, 16 Threads',
    ram: '16GB',
    ramType: 'DDR',
    storage: '1TB',
  },
  {
    id: 'LPT-008',
    brand: 'Asus',
    model: 'ROG Zephyrus G14 2023 GA402XV-N2034WS Laptop',
    priceInr: 189990,
    benchmarkScore: 89.0,
    processor: '7th Gen AMD Ryzen 9 7940HS',
    cores: 'Octa Core, 16 Threads',
    ram: '32GB',
    ramType: 'DDR5',
    storage: '1TB',
  },
];

export const mockDemands: DemandItem[] = [
  {
    id: 'DEM-401',
    requestedBy: 'Sarah Jenkins',
    department: 'Data Science',
    category: 'Hardware Workstation',
    itemName: 'ROG Zephyrus G14 (AMD Ryzen 9, 32GB RAM)',
    estCost: '₹1,89,990',
    aiRecommendation: 'Dormant inventory match available! 1 ASUS ROG Zephyrus G14 (Score: 89.0) idle in Depot Locker.',
    approvalStatus: 'Pending Finance',
    matchedAssetAvailable: true,
    suggestedAction: 'Reallocate Inventory Asset #AST-LPT-008 instead of initiating a new PO.',
  },
  {
    id: 'DEM-402',
    requestedBy: 'Daniel Rivera',
    department: 'Product Development',
    category: 'Hardware Workstation',
    itemName: 'MacBook Air M1 (8GB / 256GB SSD)',
    estCost: '₹69,990',
    aiRecommendation: 'Approved tier. Matches IT baseline hardware benchmark (Score: 69.32).',
    approvalStatus: 'Pending Manager',
    matchedAssetAvailable: true,
    suggestedAction: 'Auto-assign from Apple Pool #AST-LPT-005 in Building A.',
  },
  {
    id: 'DEM-403',
    requestedBy: 'Elena Vance',
    department: 'Software Engineering',
    category: 'Hardware Workstation',
    itemName: 'Lenovo Yoga Slim 6 (16GB LPDDR5, Core i5)',
    estCost: '₹59,729',
    aiRecommendation: 'Compliant with Developer Standard Tier. Pre-negotiated corporate price active.',
    approvalStatus: 'Approved',
    matchedAssetAvailable: false,
    suggestedAction: 'Dispatch PO to Lenovo Corporate Procurement Portal.',
  },
];

export const mockAssets: PhysicalAsset[] = [
  {
    id: 'AST-LPT-008',
    assetTag: 'ORG-HW-08828',
    name: 'Asus ROG Zephyrus G14 2023',
    brand: 'Asus',
    category: 'High-Performance Workstation',
    location: 'Building B - High-Compute Lab Desk 12',
    assignedUser: 'AI Research Team',
    status: 'Active',
    priceInr: 189990,
    benchmarkScore: 89.0,
    processor: '7th Gen AMD Ryzen 9 7940HS',
    cores: 'Octa Core, 16 Threads',
    ram: '32GB',
    ramType: 'DDR5',
    storage: '1TB SSD',
    telemetry: {
      batteryPct: 98,
      tempCelsius: 38,
      lastPing: '10 secs ago',
      signalStrength: 'Excellent (-42 dBm)',
    },
  },
  {
    id: 'AST-LPT-005',
    assetTag: 'ORG-HW-08825',
    name: 'Apple MacBook Air 2020 (M1)',
    brand: 'Apple',
    category: 'Laptops',
    location: 'Building A - Desk 402',
    assignedUser: 'Unassigned (Dormant > 30 days)',
    status: 'Dormant (Reallocatable)',
    priceInr: 69990,
    benchmarkScore: 69.32,
    processor: 'Apple M1',
    cores: 'Octa Core (4P + 4E)',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '256GB SSD',
    telemetry: {
      batteryPct: 94,
      tempCelsius: 24,
      lastPing: '2 mins ago',
      signalStrength: 'Strong (-48 dBm)',
    },
  },
  {
    id: 'AST-LPT-007',
    assetTag: 'ORG-HW-08827',
    name: 'Asus TUF A15 Gaming Laptop',
    brand: 'Asus',
    category: 'Engineering Workstation',
    location: 'Building B - IT Depot Locker 2',
    assignedUser: 'Alex Morgan',
    status: 'Active',
    priceInr: 110000,
    benchmarkScore: 71.0,
    processor: '6th Gen AMD Ryzen 7 6800H',
    cores: 'Octa Core, 16 Threads',
    ram: '16GB',
    ramType: 'DDR',
    storage: '1TB SSD',
    telemetry: {
      batteryPct: 88,
      tempCelsius: 36,
      lastPing: '5 mins ago',
      signalStrength: 'Strong (-51 dBm)',
    },
  },
  {
    id: 'AST-LPT-004',
    assetTag: 'ORG-HW-08824',
    name: 'Lenovo Yoga Slim 6 14IAP8',
    brand: 'Lenovo',
    category: 'Laptops',
    location: 'Building A - Floor 3 Design Studio',
    assignedUser: 'Sarah Jenkins',
    status: 'Active',
    priceInr: 59729,
    benchmarkScore: 66.0,
    processor: '12th Gen Intel Core i5 1240P',
    cores: '12 Cores (4P + 8E), 16 Threads',
    ram: '16GB',
    ramType: 'LPDDR5',
    storage: '512GB SSD',
    telemetry: {
      batteryPct: 100,
      tempCelsius: 29,
      lastPing: 'Just now',
      signalStrength: 'Strong (-44 dBm)',
    },
  },
  {
    id: 'AST-LPT-001',
    assetTag: 'ORG-HW-08821',
    name: 'HP Victus 15-fb0157AX Gaming Laptop',
    brand: 'HP',
    category: 'Laptops',
    location: 'Building C - Depot Rack 9',
    assignedUser: 'Unassigned (Dormant > 45 days)',
    status: 'Dormant (Reallocatable)',
    priceInr: 49900,
    benchmarkScore: 73.0,
    processor: '5th Gen AMD Ryzen 5 5600H',
    cores: 'Hexa Core, 12 Threads',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '512GB SSD',
    telemetry: {
      batteryPct: 91,
      tempCelsius: 22,
      lastPing: '15 mins ago',
      signalStrength: 'Good (-56 dBm)',
    },
  },
  {
    id: 'AST-LPT-006',
    assetTag: 'ORG-HW-08826',
    name: 'Asus Vivobook 15X 2023',
    brand: 'Asus',
    category: 'Laptops',
    location: 'Building A - Desk 108',
    assignedUser: 'Priya Sharma',
    status: 'Active',
    priceInr: 44990,
    benchmarkScore: 69.32,
    processor: '13th Gen Intel Core i3 1315U',
    cores: 'Hexa Core (2P + 4E), 8 Threads',
    ram: '8GB',
    ramType: 'DDR4',
    storage: '512GB SSD',
    telemetry: {
      batteryPct: 96,
      tempCelsius: 31,
      lastPing: '1 min ago',
      signalStrength: 'Strong (-46 dBm)',
    },
  },
];

export const mockAuditLogs: AuditLog[] = [
  {
    id: 'AUD-1001',
    timestamp: '11:45:02',
    actor: 'System AI Engine v2.4',
    role: 'Automated Governance',
    action: 'Matched Laptop Dataset to Demand',
    target: 'DEM-401 -> AST-LPT-008 (Asus ROG Zephyrus G14)',
    confidenceScore: 0.99,
  },
  {
    id: 'AUD-1002',
    timestamp: '11:32:18',
    actor: 'Sarah Livera',
    role: 'Procurement Admin',
    action: 'Approved Reallocation Request',
    target: 'DEM-402 -> AST-LPT-005 (Apple M1)',
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
