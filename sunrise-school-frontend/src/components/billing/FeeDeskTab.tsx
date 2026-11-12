/**
 * Fee desk: find a student, see everything they owe across every fee head,
 * take a payment, print the receipt, reverse a mistake, and read the ledger.
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Avatar,
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  IconButton,
  InputAdornment,
  MenuItem,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { alpha } from '@mui/material/styles';
import {
  AccountBalanceWallet as WalletIcon,
  Add as AddIcon,
  Autorenew as GenerateIcon,
  Block as CancelIcon,
  CheckCircle as CheckCircleIcon,
  Payments as PaymentsIcon,
  PersonSearch as PersonSearchIcon,
  ReceiptLong as ReceiptIcon,
  Savings as SavingsIcon,
  Search as SearchIcon,
  Send as SendIcon,
  StopCircle as StopIcon,
  Undo as UndoIcon,
  WarningAmber as WarningIcon,
} from '@mui/icons-material';
import {
  billingAPI,
  Due,
  FeeHead,
  FREQUENCIES,
  frequencyLabel,
  Ledger,
  Payment,
  PaymentDetail,
  PlanLine,
  searchStudents,
  StudentBalance,
  StudentLite,
} from '../../services/billingService';
import { Lookups } from '../../hooks/useLookups';
import {
  apiError,
  ConfirmDialog,
  ConfirmRequest,
  EmptyState,
  FieldRow,
  FormDialog,
  formatDate,
  formatMonth,
  Loading,
  money,
  Panel,
  StatCard,
  StatGrid,
  StatusChip,
  todayISO,
  useNotify,
} from '../ui';
import { brand, ease } from '../../theme';

interface Props {
  lookups: Lookups;
  heads: FeeHead[];
}

const isOpen = (due: Due) => due.status === 'PENDING' || due.status === 'PARTIAL';
const isOverdue = (due: Due) => isOpen(due) && due.due_date < todayISO();
const sum = (values: (string | number)[]) => values.reduce<number>((total, value) => total + Number(value), 0);

// ---------------------------------------------------------------------------
// Collect payment
// ---------------------------------------------------------------------------

interface CollectProps {
  open: boolean;
  student: StudentLite;
  sessionYearId: number;
  selected: Due[];
  openBalance: number;
  lookups: Lookups;
  onClose: () => void;
  onPaid: () => void;
}

const CollectPaymentDialog: React.FC<CollectProps> = ({ open, student, sessionYearId, selected, openBalance, lookups, onClose, onPaid }) => {
  const suggested = selected.length ? sum(selected.map((due) => due.balance)) : openBalance;
  const [amount, setAmount] = useState('');
  const [methodId, setMethodId] = useState<number | ''>('');
  const [date, setDate] = useState(todayISO());
  const [transactionId, setTransactionId] = useState('');
  const [remarks, setRemarks] = useState('');
  const [sendReceipt, setSendReceipt] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<PaymentDetail | null>(null);

  useEffect(() => {
    if (!open) return;
    setAmount(suggested > 0 ? suggested.toFixed(2) : '');
    setMethodId(lookups.paymentMethods[0]?.id ?? '');
    setDate(todayISO());
    setTransactionId('');
    setRemarks('');
    setSendReceipt(false);
    setError(null);
    setDone(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const method = lookups.paymentMethods.find((item) => item.id === methodId);
  const needsReference = Boolean(method?.requires_reference);
  const value = Number(amount);
  const extra = value - suggested;

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const payment = await billingAPI.collect({
        student_id: student.id,
        session_year_id: sessionYearId,
        amount: value.toFixed(2),
        payment_method_id: methodId,
        payment_date: date,
        transaction_id: transactionId.trim(),
        remarks: remarks.trim(),
        due_ids: selected.length ? selected.map((due) => due.id) : undefined,
        send_receipt: sendReceipt,
      });
      setDone(payment);
      onPaid();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <FormDialog open={open} title="Payment saved" onClose={onClose} maxWidth="xs">
        <Box sx={{ textAlign: 'center', py: 1 }}>
          <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', animation: `fadeUp 0.5s ${ease} both` }} />
          <Typography sx={{ mt: 1, fontSize: '1.6rem', fontWeight: 800 }}>{money(done.amount)}</Typography>
          <Typography color="text.secondary">Receipt {done.receipt_number}</Typography>
          {Number(done.unallocated) > 0 && (
            <Alert severity="info" sx={{ mt: 2, textAlign: 'left' }}>
              {money(done.unallocated)} was more than the dues and is kept as credit for the next dues.
            </Alert>
          )}
          {sendReceipt && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
              The receipt is being sent on WhatsApp.
            </Typography>
          )}
          <Button
            variant="contained"
            startIcon={<ReceiptIcon />}
            sx={{ mt: 2.5 }}
            onClick={() => billingAPI.openReceipt(done.id).catch((failure) => setError(apiError(failure)))}
          >
            Open receipt
          </Button>
          {error && <Alert severity="error" sx={{ mt: 2, textAlign: 'left' }}>{error}</Alert>}
        </Box>
      </FormDialog>
    );
  }

  return (
    <FormDialog
      open={open}
      title="Collect payment"
      subtitle={`${student.first_name} ${student.last_name} · ${student.admission_number}`}
      onClose={onClose}
      onSubmit={submit}
      submitLabel={value > 0 ? `Collect ${money(value)}` : 'Collect'}
      busy={busy}
      disabled={!(value > 0) || !methodId || !date || (needsReference && !transactionId.trim())}
      error={error}
    >
      <Alert severity="info" icon={<PaymentsIcon />}>
        {selected.length
          ? `Goes to the ${selected.length} selected due${selected.length > 1 ? 's' : ''} (${money(suggested)}).`
          : `Goes to the oldest dues first. Open balance: ${money(openBalance)}.`}
        {extra > 0.004 && ` ${money(extra)} is extra and will be kept as credit.`}
      </Alert>
      <FieldRow>
        <TextField
          label="Amount"
          type="number"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          required
          autoFocus
          slotProps={{ htmlInput: { min: 0.01, step: 0.01 }, input: { startAdornment: <InputAdornment position="start">₹</InputAdornment> } }}
        />
        <TextField
          label="Payment date"
          type="date"
          value={date}
          onChange={(event) => setDate(event.target.value)}
          required
          slotProps={{ inputLabel: { shrink: true }, htmlInput: { max: todayISO() } }}
        />
      </FieldRow>
      <FieldRow>
        <TextField select label="Payment method" value={methodId} onChange={(event) => setMethodId(Number(event.target.value))} required>
          {lookups.paymentMethods.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.description || item.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="Transaction / reference no."
          value={transactionId}
          onChange={(event) => setTransactionId(event.target.value)}
          required={needsReference}
          helperText={needsReference ? 'Needed for this payment method' : 'Optional'}
          slotProps={{ htmlInput: { maxLength: 100 } }}
        />
      </FieldRow>
      <TextField label="Remarks" value={remarks} onChange={(event) => setRemarks(event.target.value)} multiline minRows={2} />
      <FormControlLabel
        control={<Checkbox checked={sendReceipt} onChange={(event) => setSendReceipt(event.target.checked)} />}
        label="Send the receipt to the parent on WhatsApp"
      />
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// Reverse a payment
// ---------------------------------------------------------------------------

const ReverseDialog: React.FC<{ payment: Payment | null; lookups: Lookups; onClose: () => void; onDone: () => void }> = ({
  payment,
  lookups,
  onClose,
  onDone,
}) => {
  const [amount, setAmount] = useState('');
  const [reasonId, setReasonId] = useState<number | ''>('');
  const [remarks, setRemarks] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAmount('');
    setReasonId('');
    setRemarks('');
    setError(null);
  }, [payment]);

  const submit = async () => {
    if (!payment || !reasonId) return;
    setBusy(true);
    setError(null);
    try {
      await billingAPI.reverse(payment.id, {
        amount: amount ? Number(amount).toFixed(2) : undefined,
        reversal_reason_id: reasonId,
        remarks: remarks.trim(),
      });
      onDone();
      onClose();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  return (
    <FormDialog
      open={Boolean(payment)}
      title="Reverse payment"
      subtitle={payment ? `Receipt ${payment.receipt_number} · ${money(payment.amount)}` : undefined}
      onClose={onClose}
      onSubmit={submit}
      submitLabel="Reverse"
      submitColor="error"
      busy={busy}
      disabled={!reasonId || (amount !== '' && !(Number(amount) > 0))}
      error={error}
    >
      <Alert severity="warning">The dues this payment covered become unpaid again. The original receipt stays on record.</Alert>
      <FieldRow>
        <TextField
          label="Amount to reverse"
          type="number"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          helperText="Leave empty to reverse the whole payment"
          slotProps={{ htmlInput: { min: 0.01, step: 0.01, max: payment?.amount }, input: { startAdornment: <InputAdornment position="start">₹</InputAdornment> } }}
        />
        <TextField select label="Reason" value={reasonId} onChange={(event) => setReasonId(Number(event.target.value))} required>
          {lookups.reversalReasons.map((item) => (
            <MenuItem key={item.id} value={item.id}>
              {item.description || item.name}
            </MenuItem>
          ))}
        </TextField>
      </FieldRow>
      <TextField label="Remarks" value={remarks} onChange={(event) => setRemarks(event.target.value)} multiline minRows={2} />
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// One-off charge on a student's plan
// ---------------------------------------------------------------------------

const AddChargeDialog: React.FC<{
  open: boolean;
  studentId: number;
  sessionYearId: number;
  heads: FeeHead[];
  onClose: () => void;
  onDone: () => void;
}> = ({ open, studentId, sessionYearId, heads, onClose, onDone }) => {
  const usable = heads.filter((head) => head.is_active && !head.is_system);
  const [headId, setHeadId] = useState<number | ''>('');
  const [amount, setAmount] = useState('');
  const [frequency, setFrequency] = useState('ONE_TIME');
  const [month, setMonth] = useState(todayISO().slice(0, 7));
  const [remarks, setRemarks] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setHeadId('');
    setAmount('');
    setFrequency('ONE_TIME');
    setMonth(todayISO().slice(0, 7));
    setRemarks('');
    setError(null);
  }, [open]);

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      await billingAPI.addPlanLine(studentId, {
        session_year_id: sessionYearId,
        fee_head_id: headId,
        amount: Number(amount).toFixed(2),
        frequency,
        start_period: month ? `${month}-01` : undefined,
        remarks: remarks.trim(),
      });
      // Bill it straight away so it shows up under Dues
      await billingAPI.generateDues({ session_year_id: sessionYearId, student_id: studentId });
      onDone();
      onClose();
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setBusy(false);
    }
  };

  return (
    <FormDialog
      open={open}
      title="Add a charge"
      subtitle="For this student only, on top of the class fee structure"
      onClose={onClose}
      onSubmit={submit}
      submitLabel="Add charge"
      busy={busy}
      disabled={!headId || !(Number(amount) > 0)}
      error={error}
    >
      <FieldRow>
        <TextField select label="Fee head" value={headId} onChange={(event) => setHeadId(Number(event.target.value))} required>
          {usable.map((head) => (
            <MenuItem key={head.id} value={head.id}>
              {head.name}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="Amount"
          type="number"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          required
          slotProps={{ htmlInput: { min: 0.01, step: 0.01 }, input: { startAdornment: <InputAdornment position="start">₹</InputAdornment> } }}
        />
      </FieldRow>
      <FieldRow>
        <TextField select label="How often" value={frequency} onChange={(event) => setFrequency(event.target.value)}>
          {FREQUENCIES.map((item) => (
            <MenuItem key={item.value} value={item.value}>
              {item.label}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label={frequency === 'ONE_TIME' ? 'Bill in' : 'Starting from'}
          type="month"
          value={month}
          onChange={(event) => setMonth(event.target.value)}
          slotProps={{ inputLabel: { shrink: true } }}
        />
      </FieldRow>
      <TextField label="Remarks" value={remarks} onChange={(event) => setRemarks(event.target.value)} />
    </FormDialog>
  );
};

// ---------------------------------------------------------------------------
// The desk
// ---------------------------------------------------------------------------

const FeeDeskTab: React.FC<Props> = ({ lookups, heads }) => {
  const { notify, notifyError, node } = useNotify();
  const headName = useCallback((id: number) => heads.find((head) => head.id === id)?.name || `Head ${id}`, [heads]);

  // Student finder
  const [search, setSearch] = useState('');
  const [classId, setClassId] = useState<number | ''>('');
  const [results, setResults] = useState<StudentLite[]>([]);
  const [total, setTotal] = useState(0);
  const [searching, setSearching] = useState(false);
  const [student, setStudent] = useState<StudentLite | null>(null);

  // Selected student
  const [sessionId, setSessionId] = useState<number | null>(lookups.currentSessionId);
  const [view, setView] = useState<'dues' | 'payments' | 'ledger' | 'plan'>('dues');
  const [loading, setLoading] = useState(false);
  const [balance, setBalance] = useState<StudentBalance | null>(null);
  const [dues, setDues] = useState<Due[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [ledger, setLedger] = useState<Ledger | null>(null);
  const [plan, setPlan] = useState<PlanLine[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  const [collectOpen, setCollectOpen] = useState(false);
  const [chargeOpen, setChargeOpen] = useState(false);
  const [reversing, setReversing] = useState<Payment | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);
  const [working, setWorking] = useState(false);

  useEffect(() => {
    if (sessionId == null && lookups.currentSessionId != null) setSessionId(lookups.currentSessionId);
  }, [lookups.currentSessionId, sessionId]);

  // Search as the user types
  useEffect(() => {
    let cancelled = false;
    setSearching(true);
    const timer = setTimeout(() => {
      searchStudents({ search: search.trim(), class_filter: classId, per_page: 30 })
        .then((found) => {
          if (cancelled) return;
          setResults(found.students);
          setTotal(found.total);
        })
        .catch((failure) => !cancelled && notifyError(failure))
        .finally(() => !cancelled && setSearching(false));
    }, 300);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [search, classId, notifyError]);

  const load = useCallback(async () => {
    if (!student || sessionId == null) return;
    setLoading(true);
    try {
      const [nextBalance, nextDues, nextPayments, nextLedger, nextPlan] = await Promise.all([
        billingAPI.studentBalance(student.id),
        billingAPI.studentDues(student.id, sessionId),
        billingAPI.studentPayments(student.id, sessionId),
        billingAPI.ledger(student.id, sessionId),
        billingAPI.studentPlan(student.id, sessionId),
      ]);
      setBalance(nextBalance);
      setDues(nextDues);
      setPayments(nextPayments);
      setLedger(nextLedger);
      setPlan(nextPlan);
      setSelectedIds([]);
    } catch (failure) {
      notifyError(failure);
    } finally {
      setLoading(false);
    }
  }, [student, sessionId, notifyError]);

  useEffect(() => {
    load();
  }, [load]);

  const visibleDues = useMemo(() => dues.filter((due) => due.status !== 'CANCELLED'), [dues]);
  const openDues = useMemo(() => visibleDues.filter(isOpen), [visibleDues]);
  const openBalance = useMemo(() => sum(openDues.map((due) => due.balance)), [openDues]);
  const selected = useMemo(() => openDues.filter((due) => selectedIds.includes(due.id)), [openDues, selectedIds]);
  const reversedIds = useMemo(
    () => new Set(payments.filter((payment) => payment.kind === 'REVERSAL').map((payment) => payment.reverses_payment_id)),
    [payments]
  );

  const toggle = (id: number) => setSelectedIds((ids) => (ids.includes(id) ? ids.filter((value) => value !== id) : [...ids, id]));
  const allSelected = openDues.length > 0 && selectedIds.length === openDues.length;

  const generateForStudent = async () => {
    if (!student || sessionId == null) return;
    setWorking(true);
    try {
      const result = await billingAPI.generateDues({ session_year_id: sessionId, student_id: student.id });
      notify(result.created ? `${result.created} new due${result.created > 1 ? 's' : ''} generated (${money(result.total_amount)}).` : 'Dues are already up to date.', result.created ? 'success' : 'info');
      await load();
    } catch (failure) {
      notifyError(failure);
    } finally {
      setWorking(false);
    }
  };

  const sendReceipt = async (payment: Payment) => {
    try {
      const result = await billingAPI.sendReceipt(payment.id);
      const status: string = result?.whatsapp?.status || '';
      if (result?.whatsapp?.success || status === 'SENT') notify('Receipt sent on WhatsApp.');
      else if (status === 'NO_PHONE') notify('Receipt saved, but this student has no phone number to send it to.', 'warning');
      else if (status === 'DISABLED') notify('Receipt saved. WhatsApp sending is switched off for this school.', 'info');
      else notify(result?.upload_error ? `Receipt could not be uploaded: ${result.upload_error}` : 'Receipt saved, but WhatsApp did not accept it.', 'warning');
      load();
    } catch (failure) {
      notifyError(failure);
    }
  };

  const methodName = (id: number | null) => {
    const method = lookups.paymentMethods.find((item) => item.id === id);
    return method ? method.description || method.name : '—';
  };

  return (
    <Box sx={{ display: 'grid', gap: 3, gridTemplateColumns: { xs: '1fr', lg: '340px minmax(0, 1fr)' }, alignItems: 'start' }}>
      {/* Finder */}
      <Panel title="Find a student" subtitle={searching ? 'Searching…' : `${total} student${total === 1 ? '' : 's'}`} padded={false} sx={{ position: { lg: 'sticky' }, top: { lg: 88 } }}>
        <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          <TextField
            placeholder="Name or admission number"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            size="small"
            autoFocus
            slotProps={{ input: { startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment> } }}
          />
          <TextField select size="small" label="Class" value={classId} onChange={(event) => setClassId(event.target.value === '' ? '' : Number(event.target.value))}>
            <MenuItem value="">All classes</MenuItem>
            {lookups.classes.map((item) => (
              <MenuItem key={item.id} value={item.id}>
                {item.description || item.name}
              </MenuItem>
            ))}
          </TextField>
        </Box>
        <Box sx={{ maxHeight: { xs: 280, lg: 'calc(100vh - 330px)' }, overflowY: 'auto', px: 1, pb: 1 }}>
          {results.length === 0 && !searching && <EmptyState title="No students found" hint="Try another name or class." icon={<PersonSearchIcon />} />}
          {results.map((item) => {
            const active = student?.id === item.id;
            return (
              <Box
                key={item.id}
                component="button"
                type="button"
                onClick={() => setStudent(item)}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                  width: '100%',
                  p: 1.25,
                  mb: 0.5,
                  border: '1px solid',
                  borderColor: active ? alpha(brand.primary, 0.4) : 'transparent',
                  borderRadius: '14px',
                  background: active ? alpha(brand.primary, 0.08) : 'transparent',
                  boxShadow: active ? `0 8px 20px ${alpha(brand.primary, 0.15)}` : 'none',
                  cursor: 'pointer',
                  font: 'inherit',
                  textAlign: 'left',
                  transition: `all 0.25s ${ease}`,
                  '&:hover': { background: alpha(brand.primary, 0.06), transform: 'translateX(3px)' },
                }}
              >
                <Avatar sx={{ width: 38, height: 38, fontSize: '0.9rem', fontWeight: 700, background: active ? brand.gradient : alpha(brand.primary, 0.14), color: active ? '#fff' : 'primary.main' }}>
                  {item.first_name?.[0]}
                  {item.last_name?.[0]}
                </Avatar>
                <Box sx={{ minWidth: 0 }}>
                  <Typography noWrap sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                    {item.first_name} {item.last_name}
                  </Typography>
                  <Typography noWrap variant="caption" color="text.secondary">
                    {item.admission_number} · {item.class_name || lookups.className(item.class_id)}
                    {item.section ? ` ${item.section}` : ''}
                  </Typography>
                </Box>
              </Box>
            );
          })}
        </Box>
      </Panel>

      {/* Selected student */}
      {!student ? (
        <Panel>
          <EmptyState title="Pick a student to start" hint="Their dues for every fee head, payments and receipts appear here." icon={<PersonSearchIcon />} />
        </Panel>
      ) : (
        <Box key={student.id} sx={{ minWidth: 0 }}>
          <Panel sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
              <Avatar sx={{ width: 54, height: 54, fontWeight: 800, background: brand.gradient, boxShadow: brand.shadowGlow }}>
                {student.first_name?.[0]}
                {student.last_name?.[0]}
              </Avatar>
              <Box sx={{ flexGrow: 1, minWidth: 180 }}>
                <Typography sx={{ fontWeight: 800, fontSize: '1.15rem' }}>
                  {student.first_name} {student.last_name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {student.admission_number} · {student.class_name || lookups.className(student.class_id)}
                  {student.father_name ? ` · Father: ${student.father_name}` : ''}
                </Typography>
              </Box>
              <TextField select size="small" label="Session" value={sessionId ?? ''} onChange={(event) => setSessionId(Number(event.target.value))} sx={{ minWidth: 130 }}>
                {lookups.sessionYears.map((year) => (
                  <MenuItem key={year.id} value={year.id}>
                    {year.name}
                  </MenuItem>
                ))}
              </TextField>
              <Tooltip title="Bill this student up to this month from their fee plan">
                <span>
                  <Button variant="outlined" startIcon={<GenerateIcon />} onClick={generateForStudent} disabled={working || loading}>
                    Update dues
                  </Button>
                </span>
              </Tooltip>
              <Button variant="contained" startIcon={<PaymentsIcon />} onClick={() => setCollectOpen(true)} disabled={loading}>
                {selected.length ? `Collect ${money(sum(selected.map((due) => due.balance)))}` : 'Collect payment'}
              </Button>
            </Box>
          </Panel>

          <StatGrid min={170}>
            <StatCard label="Balance" value={money(balance?.balance)} hint={`${balance?.open_dues ?? 0} open dues, all sessions`} icon={<WalletIcon />} tone="blue" />
            <StatCard label="Overdue" value={money(balance?.overdue)} hint="Past the due date" icon={<WarningIcon />} tone={Number(balance?.overdue) > 0 ? 'red' : 'slate'} delay={60} />
            <StatCard label="Paid" value={money(balance?.total_paid)} hint={`of ${money(balance?.total_due)} billed`} icon={<CheckCircleIcon />} tone="green" delay={120} />
            <StatCard label="Credit" value={money(balance?.credit)} hint="Advance, used for the next dues" icon={<SavingsIcon />} tone="violet" delay={180} />
          </StatGrid>

          <Panel padded={false}>
            <Tabs value={view} onChange={(_, next) => setView(next)} variant="scrollable" sx={{ px: 1.5, borderBottom: '1px solid rgba(15,23,42,0.06)' }}>
              <Tab value="dues" label={`Dues (${openDues.length} open)`} />
              <Tab value="payments" label={`Payments (${payments.filter((payment) => payment.kind === 'PAYMENT').length})`} />
              <Tab value="ledger" label="Ledger" />
              <Tab value="plan" label="Fee plan" />
            </Tabs>

            {loading ? (
              <Loading />
            ) : (
              <Box key={view} className="fade-up">
                {view === 'dues' &&
                  (visibleDues.length === 0 ? (
                    <EmptyState
                      title="No dues for this session"
                      hint="Publish a fee structure and build plans, then use Update dues."
                    />
                  ) : (
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell padding="checkbox">
                              <Checkbox
                                checked={allSelected}
                                indeterminate={selectedIds.length > 0 && !allSelected}
                                onChange={() => setSelectedIds(allSelected ? [] : openDues.map((due) => due.id))}
                                disabled={openDues.length === 0}
                                slotProps={{ input: { 'aria-label': 'Select all open dues' } }}
                              />
                            </TableCell>
                            <TableCell>Fee</TableCell>
                            <TableCell>For</TableCell>
                            <TableCell>Due date</TableCell>
                            <TableCell align="right">Amount</TableCell>
                            <TableCell align="right">Paid</TableCell>
                            <TableCell align="right">Balance</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell />
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {visibleDues.map((due) => (
                            <TableRow key={due.id} hover selected={selectedIds.includes(due.id)}>
                              <TableCell padding="checkbox">
                                {isOpen(due) && <Checkbox checked={selectedIds.includes(due.id)} onChange={() => toggle(due.id)} />}
                              </TableCell>
                              <TableCell>
                                <Typography sx={{ fontWeight: 600, fontSize: '0.875rem' }}>{headName(due.fee_head_id)}</Typography>
                                {due.line_type !== 'REGULAR' && (
                                  <Typography variant="caption" color="text.secondary">
                                    {due.description || due.line_type.toLowerCase().replace('_', ' ')}
                                  </Typography>
                                )}
                              </TableCell>
                              <TableCell>{formatMonth(due.period)}</TableCell>
                              <TableCell>{formatDate(due.due_date)}</TableCell>
                              <TableCell align="right">
                                {money(due.net_amount)}
                                {Number(due.concession_amount) > 0 && (
                                  <Typography variant="caption" color="success.main" component="div">
                                    −{money(due.concession_amount)} concession
                                  </Typography>
                                )}
                              </TableCell>
                              <TableCell align="right">{money(due.paid_amount)}</TableCell>
                              <TableCell align="right" sx={{ fontWeight: 700 }}>
                                {money(due.balance)}
                              </TableCell>
                              <TableCell>
                                <StatusChip status={isOverdue(due) ? 'OVERDUE' : due.status} />
                              </TableCell>
                              <TableCell align="right">
                                {isOpen(due) && Number(due.paid_amount) === 0 && (
                                  <Tooltip title="Cancel this due">
                                    <IconButton
                                      size="small"
                                      onClick={() =>
                                        setConfirm({
                                          title: 'Cancel due',
                                          message: `Cancel ${headName(due.fee_head_id)} for ${formatMonth(due.period)} (${money(due.net_amount)})?`,
                                          confirmLabel: 'Cancel due',
                                          danger: true,
                                          reason: { label: 'Reason', required: true },
                                          onConfirm: async (reason) => {
                                            await billingAPI.cancelDue(due.id, reason);
                                            notify('Due cancelled.');
                                            load();
                                          },
                                        })
                                      }
                                    >
                                      <CancelIcon fontSize="small" />
                                    </IconButton>
                                  </Tooltip>
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ))}

                {view === 'payments' &&
                  (payments.length === 0 ? (
                    <EmptyState title="No payments yet" hint="Payments taken for this session appear here with their receipts." icon={<ReceiptIcon />} />
                  ) : (
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Date</TableCell>
                            <TableCell>Receipt</TableCell>
                            <TableCell>Method</TableCell>
                            <TableCell>Reference</TableCell>
                            <TableCell align="right">Amount</TableCell>
                            <TableCell align="right">Actions</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {[...payments].reverse().map((payment) => {
                            const reversal = payment.kind === 'REVERSAL';
                            return (
                              <TableRow key={payment.id} hover>
                                <TableCell>{formatDate(payment.payment_date)}</TableCell>
                                <TableCell>
                                  {reversal ? (
                                    <StatusChip status="REVERSAL" label={`Reversal of #${payment.reverses_payment_id}`} />
                                  ) : (
                                    <Typography sx={{ fontWeight: 600, fontSize: '0.875rem' }}>
                                      {payment.receipt_number}
                                      {reversedIds.has(payment.id) && (
                                        <Typography component="span" variant="caption" color="error.main">
                                          {' '}
                                          · reversed
                                        </Typography>
                                      )}
                                    </Typography>
                                  )}
                                </TableCell>
                                <TableCell>{reversal ? '—' : methodName(payment.payment_method_id)}</TableCell>
                                <TableCell>{payment.transaction_id || payment.remarks || '—'}</TableCell>
                                <TableCell align="right" sx={{ fontWeight: 700, color: reversal ? 'error.main' : 'success.main' }}>
                                  {money(payment.amount)}
                                </TableCell>
                                <TableCell align="right" sx={{ whiteSpace: 'nowrap' }}>
                                  {!reversal && (
                                    <>
                                      <Tooltip title="Open receipt">
                                        <IconButton size="small" color="primary" onClick={() => billingAPI.openReceipt(payment.id).catch(notifyError)}>
                                          <ReceiptIcon fontSize="small" />
                                        </IconButton>
                                      </Tooltip>
                                      <Tooltip title="Send receipt on WhatsApp">
                                        <IconButton size="small" color="success" onClick={() => sendReceipt(payment)}>
                                          <SendIcon fontSize="small" />
                                        </IconButton>
                                      </Tooltip>
                                      <Tooltip title="Reverse payment">
                                        <IconButton size="small" color="error" onClick={() => setReversing(payment)}>
                                          <UndoIcon fontSize="small" />
                                        </IconButton>
                                      </Tooltip>
                                    </>
                                  )}
                                </TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ))}

                {view === 'ledger' &&
                  (!ledger || ledger.entries.length === 0 ? (
                    <EmptyState title="Nothing in the ledger yet" />
                  ) : (
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Date</TableCell>
                            <TableCell>Entry</TableCell>
                            <TableCell align="right">Charged</TableCell>
                            <TableCell align="right">Received</TableCell>
                            <TableCell align="right">Running balance</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {ledger.entries.map((entry, index) => (
                            <TableRow key={`${entry.reference}-${index}`} hover>
                              <TableCell>{formatDate(entry.date)}</TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <StatusChip status={entry.type} />
                                  <Typography sx={{ fontSize: '0.875rem' }}>{entry.description}</Typography>
                                </Box>
                              </TableCell>
                              <TableCell align="right">{Number(entry.debit) !== 0 ? money(entry.debit) : ''}</TableCell>
                              <TableCell align="right" sx={{ color: 'success.main' }}>
                                {Number(entry.credit) !== 0 ? money(entry.credit) : ''}
                              </TableCell>
                              <TableCell align="right" sx={{ fontWeight: 700 }}>
                                {Number(entry.balance) < 0 ? `${money(-Number(entry.balance))} credit` : money(entry.balance)}
                              </TableCell>
                            </TableRow>
                          ))}
                          <TableRow sx={{ '& td': { fontWeight: 800, borderBottom: 0, background: alpha(brand.primary, 0.05) } }}>
                            <TableCell colSpan={2}>Total</TableCell>
                            <TableCell align="right">{money(ledger.total_debit)}</TableCell>
                            <TableCell align="right">{money(ledger.total_credit)}</TableCell>
                            <TableCell align="right">{money(ledger.balance)}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ))}

                {view === 'plan' && (
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap', p: 2 }}>
                      <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
                        What this student is billed: class fees from the fee structure, transport from their assignment, and any charges added here.
                      </Typography>
                      <Button variant="outlined" startIcon={<AddIcon />} onClick={() => setChargeOpen(true)}>
                        Add a charge
                      </Button>
                    </Box>
                    {plan.length === 0 ? (
                      <EmptyState title="No fee plan yet" hint="Build plans from the published fee structure on the Billing run tab." />
                    ) : (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Fee</TableCell>
                              <TableCell align="right">Amount</TableCell>
                              <TableCell>How often</TableCell>
                              <TableCell>From</TableCell>
                              <TableCell>Until</TableCell>
                              <TableCell>Comes from</TableCell>
                              <TableCell />
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {plan.map((line) => (
                              <TableRow key={line.id} hover>
                                <TableCell>
                                  <Typography sx={{ fontWeight: 600, fontSize: '0.875rem' }}>{headName(line.fee_head_id)}</Typography>
                                  {line.remarks && (
                                    <Typography variant="caption" color="text.secondary">
                                      {line.remarks}
                                    </Typography>
                                  )}
                                </TableCell>
                                <TableCell align="right">{money(line.amount)}</TableCell>
                                <TableCell>{frequencyLabel(line.frequency)}</TableCell>
                                <TableCell>{formatMonth(line.start_period)}</TableCell>
                                <TableCell>{line.end_period ? formatMonth(line.end_period) : 'End of session'}</TableCell>
                                <TableCell>
                                  <StatusChip status={line.source === 'MANUAL' ? 'DRAFT' : 'PENDING'} label={line.source === 'CLASS' ? 'Class structure' : line.source === 'TRANSPORT' ? 'Transport' : 'Added by hand'} />
                                </TableCell>
                                <TableCell align="right">
                                  {line.source === 'MANUAL' && line.is_active && (
                                    <Tooltip title="Stop this charge">
                                      <IconButton
                                        size="small"
                                        color="error"
                                        onClick={() =>
                                          setConfirm({
                                            title: 'Stop charge',
                                            message: `Stop ${headName(line.fee_head_id)} (${money(line.amount)})? Its unpaid dues are cancelled; paid ones stay.`,
                                            confirmLabel: 'Stop charge',
                                            danger: true,
                                            reason: { label: 'Reason' },
                                            onConfirm: async (reason) => {
                                              await billingAPI.endPlanLine(line.id, { reason });
                                              notify('Charge stopped.');
                                              load();
                                            },
                                          })
                                        }
                                      >
                                        <StopIcon fontSize="small" />
                                      </IconButton>
                                    </Tooltip>
                                  )}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </>
                )}
              </Box>
            )}
          </Panel>

          {sessionId != null && (
            <>
              <CollectPaymentDialog
                open={collectOpen}
                student={student}
                sessionYearId={sessionId}
                selected={selected}
                openBalance={openBalance}
                lookups={lookups}
                onClose={() => setCollectOpen(false)}
                onPaid={load}
              />
              <AddChargeDialog
                open={chargeOpen}
                studentId={student.id}
                sessionYearId={sessionId}
                heads={heads}
                onClose={() => setChargeOpen(false)}
                onDone={() => {
                  notify('Charge added.');
                  load();
                }}
              />
            </>
          )}
          <ReverseDialog
            payment={reversing}
            lookups={lookups}
            onClose={() => setReversing(null)}
            onDone={() => {
              notify('Payment reversed.');
              load();
            }}
          />
        </Box>
      )}
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
      {node}
    </Box>
  );
};

export default FeeDeskTab;
