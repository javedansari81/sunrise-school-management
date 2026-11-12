/**
 * Unified fee module (/api/v1/billing): heads, structures, plans, dues,
 * payments, receipts and reports. Money is sent and received as exact strings.
 */
import api from './api';

export type Frequency = 'MONTHLY' | 'QUARTERLY' | 'HALF_YEARLY' | 'ANNUAL' | 'ONE_TIME';
export type HeadCategory = 'ACADEMIC' | 'TRANSPORT' | 'ONE_TIME' | 'PENALTY' | 'OTHER';
export type AppliesTo = 'ALL' | 'NEW_STUDENTS' | 'EXISTING_STUDENTS';

export const FREQUENCIES: { value: Frequency; label: string }[] = [
  { value: 'MONTHLY', label: 'Monthly' },
  { value: 'QUARTERLY', label: 'Quarterly' },
  { value: 'HALF_YEARLY', label: 'Half-yearly' },
  { value: 'ANNUAL', label: 'Annual' },
  { value: 'ONE_TIME', label: 'One time' },
];
export const HEAD_CATEGORIES: { value: HeadCategory; label: string }[] = [
  { value: 'ACADEMIC', label: 'Academic' },
  { value: 'TRANSPORT', label: 'Transport' },
  { value: 'ONE_TIME', label: 'One time' },
  { value: 'PENALTY', label: 'Penalty' },
  { value: 'OTHER', label: 'Other' },
];
export const APPLIES_TO: { value: AppliesTo; label: string }[] = [
  { value: 'ALL', label: 'All students' },
  { value: 'NEW_STUDENTS', label: 'New students' },
  { value: 'EXISTING_STUDENTS', label: 'Existing students' },
];
export const frequencyLabel = (value: string) => FREQUENCIES.find((f) => f.value === value)?.label || value;

export interface FeeHead {
  id: number;
  code: string;
  name: string;
  description: string | null;
  category: HeadCategory;
  default_frequency: Frequency;
  is_system: boolean;
  sort_order: number;
  is_active: boolean;
}

export interface StructureItem {
  id?: number;
  fee_head_id: number;
  class_id: number | null;
  amount: string;
  frequency: Frequency;
  billing_months: number[] | null;
  due_day: number;
  applies_to: AppliesTo;
}

export interface FeeStructureSummary {
  id: number;
  session_year_id: number;
  name: string;
  description: string | null;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  published_at: string | null;
  created_at: string | null;
}
export interface FeeStructure extends FeeStructureSummary {
  items: StructureItem[];
}

export interface Due {
  id: number;
  student_id: number;
  session_year_id: number;
  fee_head_id: number;
  line_type: string;
  period: string;
  due_date: string;
  description: string | null;
  gross_amount: string;
  concession_amount: string;
  net_amount: string;
  paid_amount: string;
  balance: string;
  status: 'PENDING' | 'PARTIAL' | 'PAID' | 'CANCELLED' | 'WAIVED';
  cancel_reason: string | null;
  fee_head_name?: string;
}

export interface Payment {
  id: number;
  student_id: number;
  session_year_id: number;
  kind: 'PAYMENT' | 'REVERSAL';
  receipt_number: string | null;
  amount: string;
  payment_method_id: number | null;
  payment_date: string;
  transaction_id: string | null;
  remarks: string | null;
  reverses_payment_id: number | null;
  receipt_url: string | null;
}
export interface PaymentDetail extends Payment {
  allocated: string;
  reversed: string;
  unallocated: string;
}

export interface StudentBalance {
  student_id: number;
  total_due: string;
  total_paid: string;
  balance: string;
  overdue: string;
  credit: string;
  open_dues: number;
}

export interface PlanLine {
  id: number;
  fee_head_id: number;
  amount: string;
  frequency: Frequency;
  due_day: number;
  start_period: string;
  end_period: string | null;
  source: 'CLASS' | 'TRANSPORT' | 'MANUAL';
  is_active: boolean;
  remarks: string | null;
}

export interface LedgerEntry {
  date: string;
  type: 'DUE' | 'PAYMENT' | 'REVERSAL';
  reference: string | null;
  description: string;
  debit: string;
  credit: string;
  balance: string;
  status: string | null;
}
export interface Ledger {
  student_id: number;
  student_name: string;
  admission_number: string;
  total_debit: string;
  total_credit: string;
  balance: string;
  entries: LedgerEntry[];
}

export interface CollectionReport {
  date_from: string;
  date_to: string;
  received: string;
  reversed: string;
  net: string;
  payments: number;
  by_day: { date: string; amount: string }[];
  by_method: { payment_method_id: number | null; method: string | null; amount: string }[];
  by_head: { fee_head_id: number; code: string; name: string; amount: string }[];
  not_allocated: string;
}

export interface PendingByClass {
  session_year_id: number;
  as_of: string;
  classes: { class_id: number | null; class_name: string; students_with_dues: number; pending: string; overdue: string }[];
  total_pending: string;
  total_overdue: string;
}

export interface MyStatement {
  student_id: number;
  student_name: string;
  admission_number: string;
  balance: StudentBalance;
  dues: Due[];
  payments: Payment[];
}

const data = <T>(promise: Promise<{ data: T }>): Promise<T> => promise.then((response) => response.data);
const clean = (params: Record<string, any>) =>
  Object.fromEntries(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''));

/** Open a PDF that needs the login token: fetch it, then show it in a new tab. */
const openPdf = async (url: string) => {
  const tab = window.open('', '_blank');
  try {
    const response = await api.get(url, { responseType: 'blob', timeout: 30000 });
    const blobUrl = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    if (tab) tab.location.href = blobUrl;
    else window.location.href = blobUrl;
    setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
  } catch (error) {
    tab?.close();
    throw error;
  }
};

export const billingAPI = {
  // Fee heads
  listHeads: (includeInactive = false) =>
    data<FeeHead[]>(api.get('/billing/fee-heads', { params: { include_inactive: includeInactive } })),
  createHead: (body: Partial<FeeHead>) => data<FeeHead>(api.post('/billing/fee-heads', body)),
  updateHead: (id: number, body: Partial<FeeHead>) => data<FeeHead>(api.patch(`/billing/fee-heads/${id}`, body)),
  deleteHead: (id: number) => api.delete(`/billing/fee-heads/${id}`),

  // Fee structures
  listStructures: (sessionYearId?: number) =>
    data<FeeStructureSummary[]>(api.get('/billing/fee-structures', { params: clean({ session_year_id: sessionYearId }) })),
  getStructure: (id: number) => data<FeeStructure>(api.get(`/billing/fee-structures/${id}`)),
  createStructure: (body: { session_year_id: number; name: string; description?: string | null; items: StructureItem[] }) =>
    data<FeeStructure>(api.post('/billing/fee-structures', body)),
  updateStructure: (id: number, body: { name?: string; description?: string | null }) =>
    data<FeeStructure>(api.patch(`/billing/fee-structures/${id}`, body)),
  replaceItems: (id: number, items: StructureItem[]) =>
    data<FeeStructure>(api.put(`/billing/fee-structures/${id}/items`, items)),
  publishStructure: (id: number) => data<FeeStructure>(api.post(`/billing/fee-structures/${id}/publish`)),
  archiveStructure: (id: number) => data<FeeStructure>(api.post(`/billing/fee-structures/${id}/archive`)),
  copyStructure: (id: number, body: { session_year_id?: number; name?: string }) =>
    data<FeeStructure>(api.post(`/billing/fee-structures/${id}/copy`, body)),
  deleteStructure: (id: number) => api.delete(`/billing/fee-structures/${id}`),

  // Plans, dues, late fees
  buildPlans: (body: { session_year_id: number; class_id?: number | null; effective_from?: string | null }) =>
    data<any>(api.post('/billing/plans/build', clean(body), { timeout: 120000 })),
  generateDues: (body: {
    session_year_id: number;
    class_id?: number | null;
    student_id?: number | null;
    through_period?: string | null;
  }) => data<any>(api.post('/billing/dues/generate', clean(body), { timeout: 120000 })),
  applyLateFees: (body: { as_of?: string | null; session_year_id?: number | null }) =>
    data<any>(api.post('/billing/late-fees/apply', clean(body), { timeout: 120000 })),
  studentPlan: (studentId: number, sessionYearId: number) =>
    data<PlanLine[]>(api.get(`/billing/students/${studentId}/plan`, { params: { session_year_id: sessionYearId } })),
  addPlanLine: (studentId: number, body: Record<string, any>) =>
    data<PlanLine>(api.post(`/billing/students/${studentId}/plan-lines`, clean(body))),
  endPlanLine: (lineId: number, body: { last_period?: string | null; reason?: string }) =>
    data<PlanLine>(api.post(`/billing/plan-lines/${lineId}/end`, clean(body))),
  studentDues: (studentId: number, sessionYearId?: number) =>
    data<Due[]>(api.get(`/billing/students/${studentId}/dues`, { params: clean({ session_year_id: sessionYearId }) })),
  cancelDue: (dueId: number, reason: string) => data<Due>(api.post(`/billing/dues/${dueId}/cancel`, { reason })),

  // Payments
  collect: (body: Record<string, any>) =>
    data<PaymentDetail>(api.post('/billing/payments', clean(body), { timeout: 30000 })),
  reverse: (paymentId: number, body: { amount?: string; reversal_reason_id: number; remarks?: string }) =>
    data<Payment>(api.post(`/billing/payments/${paymentId}/reverse`, clean(body))),
  studentPayments: (studentId: number, sessionYearId?: number) =>
    data<Payment[]>(api.get(`/billing/students/${studentId}/payments`, { params: clean({ session_year_id: sessionYearId }) })),
  studentBalance: (studentId: number) => data<StudentBalance>(api.get(`/billing/students/${studentId}/balance`)),
  openReceipt: (paymentId: number) => openPdf(`/billing/payments/${paymentId}/receipt.pdf`),
  sendReceipt: (paymentId: number) =>
    data<any>(api.post(`/billing/payments/${paymentId}/receipt/send`, {}, { timeout: 60000 })),

  // Reports
  ledger: (studentId: number, sessionYearId?: number) =>
    data<Ledger>(api.get(`/billing/students/${studentId}/ledger`, { params: clean({ session_year_id: sessionYearId }) })),
  collectionReport: (dateFrom: string, dateTo: string) =>
    data<CollectionReport>(api.get('/billing/reports/collection', { params: { date_from: dateFrom, date_to: dateTo } })),
  pendingByClass: (sessionYearId: number) =>
    data<PendingByClass>(api.get('/billing/reports/pending-by-class', { params: { session_year_id: sessionYearId } })),
  consistency: () => data<any>(api.get('/billing/reports/consistency', { timeout: 60000 })),

  // A student's own fees
  myStatement: (sessionYearId?: number) =>
    data<MyStatement>(api.get('/billing/my/statement', { params: clean({ session_year_id: sessionYearId }) })),
  openMyReceipt: (paymentId: number) => openPdf(`/billing/my/payments/${paymentId}/receipt.pdf`),
};

export interface StudentLite {
  id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  class_id: number | null;
  class_name?: string | null;
  section?: string | null;
  father_name?: string | null;
  is_active?: boolean;
}

/** Find students by name or admission number (used by the fee desk and transport). */
export const searchStudents = (params: {
  search?: string;
  class_filter?: number | '';
  session_year_id?: number | '';
  per_page?: number;
}) =>
  api
    .get('/students', { params: clean({ is_active: true, per_page: 25, ...params }) })
    .then((response) => ({ students: response.data.students as StudentLite[], total: response.data.total as number }));
