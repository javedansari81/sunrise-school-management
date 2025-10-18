import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Typography,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  Box,
  Alert,
  Grid
} from '@mui/material';
import transportService, {
  EnhancedStudentTransportSummary,
  TransportType,
  TransportDistanceSlab
} from '../../../services/transportService';

interface EnrollDialogProps {
  open: boolean;
  onClose: () => void;
  student: EnhancedStudentTransportSummary | null;
  transportTypes: TransportType[];
  sessionYear: string;
  configuration: any;
  onSuccess: () => void;
  onError: (message: string) => void;
}

const EnrollDialog: React.FC<EnrollDialogProps> = ({
  open,
  onClose,
  student,
  transportTypes,
  sessionYear,
  configuration,
  onSuccess,
  onError
}) => {
  const [loading, setLoading] = useState(false);
  const [distanceSlabs, setDistanceSlabs] = useState<TransportDistanceSlab[]>([]);

  // Form state
  const [transportTypeId, setTransportTypeId] = useState<number>(0);
  const [enrollmentDate, setEnrollmentDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [distanceKm, setDistanceKm] = useState<string>('');
  const [pickupLocation, setPickupLocation] = useState<string>('');
  const [dropLocation, setDropLocation] = useState<string>('');
  const [calculatedFee, setCalculatedFee] = useState<number>(0);
  const [enableMonthlyTracking, setEnableMonthlyTracking] = useState<boolean>(true);

  // Load distance slabs when transport type changes
  useEffect(() => {
    if (transportTypeId) {
      loadDistanceSlabs(transportTypeId);
    }
  }, [transportTypeId]);

  // Calculate fee when distance or transport type changes
  useEffect(() => {
    calculateFee();
  }, [transportTypeId, distanceKm, distanceSlabs]);

  const loadDistanceSlabs = async (typeId: number) => {
    try {
      const slabs = await transportService.getDistanceSlabs(typeId);
      setDistanceSlabs(slabs);
    } catch (err) {
      console.error('Error loading distance slabs:', err);
    }
  };

  const calculateFee = useCallback(() => {
    const selectedType = transportTypes.find(t => t.id === transportTypeId);
    if (!selectedType) {
      setCalculatedFee(0);
      return;
    }

    // If no distance slabs (E-Rickshaw), use base fee
    if (distanceSlabs.length === 0) {
      setCalculatedFee(Number(selectedType.base_monthly_fee || 0));
      return;
    }

    // Find applicable slab based on distance
    const distance = parseFloat(distanceKm) || 0;
    if (distance === 0) {
      setCalculatedFee(Number(selectedType.base_monthly_fee || 0));
      return;
    }

    const applicableSlab = distanceSlabs.find(
      slab => distance >= slab.distance_from_km && distance <= slab.distance_to_km
    );

    if (applicableSlab) {
      setCalculatedFee(Number(applicableSlab.monthly_fee || 0));
    } else {
      // Use the highest slab if distance exceeds all slabs
      const maxSlab = distanceSlabs.reduce((max, slab) =>
        slab.distance_to_km > max.distance_to_km ? slab : max
      );
      setCalculatedFee(Number(maxSlab.monthly_fee || 0));
    }
  }, [transportTypes, transportTypeId, distanceSlabs, distanceKm]);

  const handleSubmit = async () => {
    if (!student || !transportTypeId) {
      onError('Please select a transport type');
      return;
    }

    if (calculatedFee === 0) {
      onError('Please wait for fee calculation or enter distance for Van transport');
      return;
    }

    const sessionYearObj = configuration?.session_years?.find(
      (y: any) => y.name === sessionYear
    );
    if (!sessionYearObj) {
      onError('Invalid session year');
      return;
    }

    setLoading(true);
    try {
      // Enroll student
      const enrollment = await transportService.enrollStudent({
        student_id: student.student_id,
        session_year_id: sessionYearObj.id,
        transport_type_id: transportTypeId,
        enrollment_date: enrollmentDate,
        monthly_fee: calculatedFee,
        distance_km: distanceKm ? parseFloat(distanceKm) : undefined,
        pickup_location: pickupLocation || undefined,
        drop_location: dropLocation || undefined
      });

      // Enable monthly tracking if requested
      if (enableMonthlyTracking) {
        // Extract start year from session year (e.g., "Academic Year 2025-26" -> 2025)
        const yearMatch = sessionYear.match(/\d{4}/);
        const startYear = yearMatch ? parseInt(yearMatch[0]) : new Date().getFullYear();

        await transportService.enableMonthlyTracking({
          enrollment_ids: [enrollment.id],
          start_month: 4, // April (academic year starts in April)
          start_year: startYear
        });
      }

      onSuccess();
    } catch (err: any) {
      console.error('Error enrolling student:', err);

      // Handle validation errors (422)
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;

        // If detail is an array of validation errors
        if (Array.isArray(detail)) {
          const errorMessages = detail.map((error: any) => {
            const field = error.loc?.join('.') || 'field';
            return `${field}: ${error.msg}`;
          }).join(', ');
          onError(`Validation error: ${errorMessages}`);
        } else if (typeof detail === 'string') {
          onError(detail);
        } else {
          onError('Failed to enroll student');
        }
      } else {
        onError(err.message || 'Failed to enroll student');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      // Reset form
      setTransportTypeId(0);
      setEnrollmentDate(new Date().toISOString().split('T')[0]);
      setDistanceKm('');
      setPickupLocation('');
      setDropLocation('');
      setCalculatedFee(0);
      setEnableMonthlyTracking(true);
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        Enroll Student in Transport Service
      </DialogTitle>
      <DialogContent>
        {student && (
          <Box sx={{ mb: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              Student Details
            </Typography>
            <Typography variant="body1">
              <strong>{student.student_name}</strong> (Roll: {student.admission_number})
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Class: {student.class_name} | Session: {student.session_year}
            </Typography>
          </Box>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <FormControl fullWidth required>
              <InputLabel>Transport Type</InputLabel>
              <Select
                value={transportTypeId}
                label="Transport Type"
                onChange={(e) => setTransportTypeId(Number(e.target.value))}
                disabled={loading}
              >
                <MenuItem value={0}>Select Transport Type</MenuItem>
                {transportTypes.map((type) => (
                  <MenuItem key={type.id} value={type.id}>
                    {type.description} (Base: ₹{type.base_monthly_fee})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              required
              type="date"
              label="Enrollment Date"
              value={enrollmentDate}
              onChange={(e) => setEnrollmentDate(e.target.value)}
              disabled={loading}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          {distanceSlabs.length > 0 && (
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="number"
                label="Distance (KM)"
                value={distanceKm}
                onChange={(e) => setDistanceKm(e.target.value)}
                disabled={loading}
                inputProps={{ min: 0, step: 0.1 }}
                helperText="Distance from school to pickup location"
              />
            </Grid>
          )}

          <Grid size={{ xs: 12, sm: distanceSlabs.length > 0 ? 6 : 12 }}>
            <TextField
              fullWidth
              label="Calculated Monthly Fee"
              value={`₹${Number(calculatedFee || 0).toFixed(2)}`}
              disabled
              InputProps={{ readOnly: true }}
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Pickup Location"
              value={pickupLocation}
              onChange={(e) => setPickupLocation(e.target.value)}
              disabled={loading}
              placeholder="Enter pickup location"
            />
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              label="Drop Location"
              value={dropLocation}
              onChange={(e) => setDropLocation(e.target.value)}
              disabled={loading}
              placeholder="Enter drop location"
            />
          </Grid>

          {distanceSlabs.length > 0 && (
            <Grid size={{ xs: 12 }}>
              <Alert severity="info" sx={{ mt: 1 }}>
                <Typography variant="body2" fontWeight="bold">
                  Distance Slabs:
                </Typography>
                {distanceSlabs.map((slab, index) => (
                  <Typography key={index} variant="body2">
                    {slab.distance_from_km} - {slab.distance_to_km} KM: ₹{slab.monthly_fee}
                  </Typography>
                ))}
              </Alert>
            </Grid>
          )}
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading || !transportTypeId}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? 'Enrolling...' : 'Enroll & Enable Tracking'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default EnrollDialog;

