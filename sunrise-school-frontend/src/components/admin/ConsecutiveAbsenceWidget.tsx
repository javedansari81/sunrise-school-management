import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  CircularProgress,
  IconButton,
  Collapse,
  TextField,
  MenuItem,
  Link,
  Divider,
} from '@mui/material';
import {
  ExpandMore,
  Warning as WarningIcon,
  Phone as PhoneIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import attendanceService, {
  ConsecutiveAbsenceResponse,
  ConsecutiveAbsentStudent,
  ClassConsecutiveAbsences,
} from '../../services/attendanceService';
import { configurationService } from '../../services/configurationService';

interface ConsecutiveAbsenceWidgetProps {
  sessionYearId: number;
  expanded: boolean;
  onToggleExpand: () => void;
}

const ConsecutiveAbsenceWidget: React.FC<ConsecutiveAbsenceWidgetProps> = ({
  sessionYearId,
  expanded,
  onToggleExpand,
}) => {
  const [data, setData] = useState<ConsecutiveAbsenceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedClassId, setSelectedClassId] = useState<number | ''>('');
  const [expandedStudent, setExpandedStudent] = useState<number | false>(false);

  // Get classes from configuration service - same pattern as MetadataDropdown
  const getClasses = () => {
    // Try to get configuration from different services
    const feeConfig = configurationService.getServiceConfiguration('fee-management');
    const studentConfig = configurationService.getServiceConfiguration('student-management');
    const leaveConfig = configurationService.getServiceConfiguration('leave-management');
    const expenseConfig = configurationService.getServiceConfiguration('expense-management');
    const teacherConfig = configurationService.getServiceConfiguration('teacher-management');
    const attendanceConfig = configurationService.getServiceConfiguration('attendance-management');
    const commonConfig = configurationService.getServiceConfiguration('common');

    const configs = [feeConfig, studentConfig, leaveConfig, expenseConfig, teacherConfig, attendanceConfig, commonConfig].filter(Boolean);

    for (const config of configs) {
      if (config && (config as any).classes) {
        return (config as any).classes;
      }
    }
    return [];
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await attendanceService.getConsecutiveAbsences(
        sessionYearId,
        selectedClassId || undefined,
        3
      );
      setData(response);
    } catch (err: any) {
      console.error('Error loading consecutive absences:', err);
      // Set empty data instead of error for better UX
      setData({ total_students: 0, min_absent_days: 3, as_of_date: new Date().toISOString().split('T')[0], by_class: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionYearId) {
      loadData();
    }
  }, [sessionYearId, selectedClassId]);

  const handleStudentExpand = (studentId: number) => (
    _event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpandedStudent(isExpanded ? studentId : false);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const renderPhoneLink = (phone: string | undefined) => {
    if (!phone) return <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem' }}>--</Typography>;
    return (
      <Link href={`tel:${phone}`} sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.8rem' }}>
        <PhoneIcon sx={{ fontSize: 14 }} />
        {phone}
      </Link>
    );
  };

  const renderStudentDetails = (student: ConsecutiveAbsentStudent) => (
    <Box sx={{ pl: 2, pr: 2, pb: 1 }}>
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5 }}>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>Father</Typography>
          <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '0.8rem' }}>{student.father_name || '--'}</Typography>
          {renderPhoneLink(student.father_phone)}
        </Box>
        <Box>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>Mother</Typography>
          <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '0.8rem' }}>{student.mother_name || '--'}</Typography>
          {renderPhoneLink(student.mother_phone)}
        </Box>
      </Box>
      {student.guardian_name && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>Guardian</Typography>
          <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '0.8rem' }}>{student.guardian_name}</Typography>
          {renderPhoneLink(student.guardian_phone)}
        </Box>
      )}
      <Divider sx={{ my: 1 }} />
      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
          Last Present: {student.last_present_date ? formatDate(student.last_present_date) : 'N/A'}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
          Absent Since: {formatDate(student.absent_from_date)}
        </Typography>
      </Box>
    </Box>
  );

  const renderStudentRow = (student: ConsecutiveAbsentStudent) => (
    <Accordion
      key={student.student_id}
      expanded={expandedStudent === student.student_id}
      onChange={handleStudentExpand(student.student_id)}
      sx={{ '&:before': { display: 'none' }, boxShadow: 'none', borderBottom: '1px solid #e0e0e0' }}
    >
      <AccordionSummary expandIcon={<ExpandMore />} sx={{ minHeight: 40, '& .MuiAccordionSummary-content': { my: 0.5 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, width: '100%', flexWrap: 'wrap' }}>
          <PersonIcon sx={{ color: 'text.secondary', fontSize: 18 }} />
          <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '0.8rem', minWidth: 120 }}>
            {student.student_name}
          </Typography>
          <Chip label={`Roll: ${student.roll_number || 'N/A'}`} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.65rem' }} />
          <Chip label={`${student.consecutive_absent_days} days`} size="small" color="error" sx={{ height: 20, fontSize: '0.65rem' }} />
          {student.has_pending_leave && (
            <Chip label="Leave Pending" size="small" color="warning" sx={{ height: 20, fontSize: '0.65rem' }} />
          )}
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ pt: 0 }}>{renderStudentDetails(student)}</AccordionDetails>
    </Accordion>
  );

  const renderClassGroup = (classGroup: ClassConsecutiveAbsences) => (
    <Accordion key={classGroup.class_id} defaultExpanded={classGroup.student_count <= 3}>
      <AccordionSummary expandIcon={<ExpandMore />} sx={{ minHeight: 36 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" fontWeight="medium" sx={{ fontSize: '0.85rem' }}>{classGroup.class_name}</Typography>
          <Chip label={`${classGroup.student_count}`} size="small" color="error" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 0 }}>{classGroup.students.map(renderStudentRow)}</AccordionDetails>
    </Accordion>
  );

  const totalStudents = data?.total_students || 0;
  const changeText = totalStudents > 0
    ? `${data?.by_class.length || 0} Classes Affected`
    : 'All students attending regularly';

  return (
    <Card
      sx={{
        transition: 'all 0.3s ease-in-out',
        '&:hover': { boxShadow: { xs: 2, sm: 4 }, transform: 'translateY(-2px)' },
      }}
    >
      <CardContent sx={{ p: { xs: 1.5, sm: 2, md: 2.5 }, '&:last-child': { pb: { xs: 1.5, sm: 2, md: 2.5 } } }}>
        {/* Card Header - Same design as other dashboard cards */}
        <Box display="flex" alignItems="flex-start" justifyContent="space-between" mb={{ xs: 1, sm: 1.5 }}>
          <Box display="flex" alignItems="flex-start" gap={{ xs: 1.5, sm: 2 }} flex={1}>
            {/* Icon */}
            <Box
              sx={{
                backgroundColor: '#d32f2f',
                color: 'white',
                borderRadius: '50%',
                p: { xs: 1, sm: 1.25 },
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                '& .MuiSvgIcon-root': { fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' } }
              }}
            >
              <WarningIcon fontSize="large" />
            </Box>
            {/* Info */}
            <Box flex={1} minWidth={0}>
              <Typography
                variant="h4"
                fontWeight="bold"
                sx={{ fontSize: { xs: '1.5rem', sm: '1.75rem', md: '2rem' }, lineHeight: 1.2, mb: { xs: 0.25, sm: 0.5 } }}
              >
                {loading ? '...' : totalStudents.toString()}
              </Typography>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ fontSize: { xs: '0.875rem', sm: '0.95rem', md: '1rem' }, fontWeight: 500, mb: { xs: 0.25, sm: 0.5 } }}
              >
                Absence Alerts
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontSize: { xs: '0.7rem', sm: '0.8rem' }, lineHeight: 1.3 }}>
                {loading ? 'Loading...' : changeText}
              </Typography>
            </Box>
          </Box>
          {/* Expand/Collapse Button */}
          <IconButton
            size="small"
            onClick={(e) => { e.stopPropagation(); onToggleExpand(); }}
            sx={{ transition: 'transform 0.3s ease', transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)', flexShrink: 0, ml: 1 }}
          >
            <ExpandMore />
          </IconButton>
        </Box>

        {/* Expandable Details Section */}
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px solid #e0e0e0' }}>
            {/* Class Filter */}
            <Box sx={{ mb: 1.5, display: 'flex', justifyContent: 'flex-end' }}>
              <TextField
                select
                label="Filter by Class"
                value={selectedClassId}
                onChange={(e) => setSelectedClassId(e.target.value === '' ? '' : Number(e.target.value))}
                size="small"
                sx={{ minWidth: 140 }}
              >
                <MenuItem value="">All Classes</MenuItem>
                {getClasses().map((cls: any) => (
                  <MenuItem key={cls.id} value={cls.id}>{cls.description || cls.name}</MenuItem>
                ))}
              </TextField>
            </Box>

            {/* Content */}
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                <CircularProgress size={24} />
              </Box>
            ) : totalStudents === 0 ? (
              <Typography variant="body2" color="success.main" sx={{ textAlign: 'center', py: 2, fontSize: '0.85rem' }}>
                ✓ No students with 3+ consecutive absences
              </Typography>
            ) : (
              <Box sx={{ maxHeight: 280, overflow: 'auto' }}>
                {data?.by_class.map(renderClassGroup)}
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default ConsecutiveAbsenceWidget;

