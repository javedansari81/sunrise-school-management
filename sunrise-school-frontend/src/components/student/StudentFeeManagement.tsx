/** A student's own fees: what is owed, what was paid, and the receipts. */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  IconButton,
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
import {
  AccountBalanceWallet as WalletIcon,
  CheckCircle as PaidIcon,
  ReceiptLong as ReceiptIcon,
  Savings as SavingsIcon,
  WarningAmber as WarningIcon,
} from '@mui/icons-material';
import { billingAPI, Due, MyStatement } from '../../services/billingService';
import { useServiceConfiguration } from '../../contexts/ConfigurationContext';
import { configurationService } from '../../services/configurationService';
import { apiError, EmptyState, formatDate, formatMonth, Loading, money, PageHero, Panel, StatCard, StatGrid, StatusChip, todayISO, useNotify } from '../ui';

const isOpen = (due: Due) => due.status === 'PENDING' || due.status === 'PARTIAL';

const StudentFeeManagement: React.FC = () => {
  const { isLoaded } = useServiceConfiguration('fee-management');
  const { notifyError, node } = useNotify();
  const [sessionId, setSessionId] = useState<number | ''>('');
  const [statement, setStatement] = useState<MyStatement | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'dues' | 'payments'>('dues');

  const sessionYears = useMemo(
    () => (isLoaded ? configurationService.getServiceConfiguration('fee-management')?.session_years || [] : []),
    [isLoaded]
  );

  useEffect(() => {
    if (sessionId === '' && sessionYears.length) {
      setSessionId((sessionYears.find((year) => year.is_current) || sessionYears[sessionYears.length - 1]).id);
    }
  }, [sessionYears, sessionId]);

  const load = useCallback(async () => {
    if (sessionId === '') return;
    setLoading(true);
    try {
      setStatement(await billingAPI.myStatement(sessionId));
      setError(null);
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    load();
  }, [load]);

  const balance = statement?.balance;
  const today = todayISO();
  const payments = statement?.payments.filter((payment) => payment.kind === 'PAYMENT') || [];

  return (
    <>
      <PageHero
        icon={<WalletIcon />}
        title="My fees"
        subtitle={statement ? `${statement.student_name} · ${statement.admission_number}` : 'Everything you owe and everything you have paid'}
        actions={
          sessionYears.length > 0 && (
            <TextField
              select
              size="small"
              value={sessionId}
              onChange={(event) => setSessionId(Number(event.target.value))}
              sx={{ minWidth: 130, '& .MuiOutlinedInput-root': { background: 'rgba(255,255,255,0.92)' } }}
              slotProps={{ htmlInput: { 'aria-label': 'Session' } }}
            >
              {sessionYears.map((year) => (
                <MenuItem key={year.id} value={year.id}>
                  {year.name}
                </MenuItem>
              ))}
            </TextField>
          )
        }
      />

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {loading && !statement ? (
        <Loading />
      ) : statement ? (
        <>
          <StatGrid min={180}>
            <StatCard label="To pay" value={money(balance?.balance)} hint={`${balance?.open_dues ?? 0} open dues`} icon={<WalletIcon />} tone="blue" />
            <StatCard label="Overdue" value={money(balance?.overdue)} hint="Past the due date" icon={<WarningIcon />} tone={Number(balance?.overdue) > 0 ? 'red' : 'slate'} delay={60} />
            <StatCard label="Paid so far" value={money(balance?.total_paid)} hint={`of ${money(balance?.total_due)} billed`} icon={<PaidIcon />} tone="green" delay={120} />
            {Number(balance?.credit) > 0 && <StatCard label="Advance" value={money(balance?.credit)} hint="Used for your next dues" icon={<SavingsIcon />} tone="violet" delay={180} />}
          </StatGrid>

          <Panel padded={false}>
            <Tabs value={view} onChange={(_, next) => setView(next)} sx={{ px: 1.5, borderBottom: '1px solid rgba(15,23,42,0.06)' }}>
              <Tab value="dues" label={`Fees (${statement.dues.length})`} />
              <Tab value="payments" label={`Payments (${payments.length})`} />
            </Tabs>
            <Box key={view} className="fade-up">
              {view === 'dues' &&
                (statement.dues.length === 0 ? (
                  <EmptyState title="No fees billed for this session yet" />
                ) : (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Fee</TableCell>
                          <TableCell>For</TableCell>
                          <TableCell>Due date</TableCell>
                          <TableCell align="right">Amount</TableCell>
                          <TableCell align="right">Paid</TableCell>
                          <TableCell align="right">Balance</TableCell>
                          <TableCell>Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {statement.dues.map((due) => (
                          <TableRow key={due.id} hover>
                            <TableCell sx={{ fontWeight: 600 }}>{due.fee_head_name || due.description || 'Fee'}</TableCell>
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
                              <StatusChip status={isOpen(due) && due.due_date < today ? 'OVERDUE' : due.status} />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ))}

              {view === 'payments' &&
                (payments.length === 0 ? (
                  <EmptyState title="No payments in this session yet" icon={<ReceiptIcon />} />
                ) : (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Receipt</TableCell>
                          <TableCell align="right">Amount</TableCell>
                          <TableCell align="right">Receipt</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {[...payments].reverse().map((payment) => (
                          <TableRow key={payment.id} hover>
                            <TableCell>{formatDate(payment.payment_date)}</TableCell>
                            <TableCell sx={{ fontWeight: 600 }}>{payment.receipt_number}</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 700, color: 'success.main' }}>
                              {money(payment.amount)}
                            </TableCell>
                            <TableCell align="right">
                              <Tooltip title="Open receipt">
                                <IconButton size="small" color="primary" onClick={() => billingAPI.openMyReceipt(payment.id).catch(notifyError)}>
                                  <ReceiptIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ))}
            </Box>
          </Panel>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Fees are paid at the school office. Amounts shown under To pay and Overdue cover every session.
          </Typography>
        </>
      ) : null}
      {node}
    </>
  );
};

export default StudentFeeManagement;
