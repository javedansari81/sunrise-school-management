/**
 * A student's brothers and sisters at the school: see who is linked, confirm
 * the ones the system suggests, link anyone else, or remove a wrong link.
 * Linked siblings are what the sibling concession counts.
 */
import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Autocomplete, Avatar, Box, Button, CircularProgress, IconButton, TextField, Tooltip, Typography } from '@mui/material';
import { alpha } from '@mui/material/styles';
import { FamilyRestroom as FamilyIcon, Link as LinkIcon, LinkOff as UnlinkIcon } from '@mui/icons-material';
import { studentSiblingsAPI } from '../../services/api';
import { searchStudents, StudentLite } from '../../services/billingService';
import { apiError, ConfirmDialog, ConfirmRequest, formatDate } from '../ui';
import { brand, ease } from '../../theme';

interface Props {
  studentId: number;
  /** Called after a link or unlink with every student whose family changed. */
  onChanged?: (studentIds: number[]) => void;
  readOnly?: boolean;
}

interface Person {
  id: number;
  name: string;
  admissionNumber: string;
  className: string;
  dateOfBirth?: string | null;
}

const PersonRow: React.FC<{ person: Person; tone: string; action?: React.ReactNode; note?: string }> = ({ person, tone, action, note }) => (
  <Box
    sx={{
      display: 'flex',
      alignItems: 'center',
      gap: 1.5,
      p: 1.25,
      borderRadius: '14px',
      border: `1px solid ${alpha(tone, 0.25)}`,
      background: alpha(tone, 0.05),
      animation: `fadeUp 0.35s ${ease} both`,
      transition: `transform 0.3s ${ease}, box-shadow 0.3s ${ease}`,
      '&:hover': { transform: 'translateX(3px)', boxShadow: `0 8px 20px ${alpha(tone, 0.15)}` },
    }}
  >
    <Avatar sx={{ width: 36, height: 36, fontSize: '0.85rem', fontWeight: 700, color: '#fff', background: tone }}>
      {person.name
        .split(' ')
        .map((part) => part[0])
        .slice(0, 2)
        .join('')}
    </Avatar>
    <Box sx={{ flexGrow: 1, minWidth: 0 }}>
      <Typography noWrap sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
        {person.name}
      </Typography>
      <Typography noWrap variant="caption" color="text.secondary">
        {[person.admissionNumber, person.className, person.dateOfBirth && `born ${formatDate(person.dateOfBirth)}`, note].filter(Boolean).join(' · ')}
      </Typography>
    </Box>
    {action}
  </Box>
);

const SiblingsManager: React.FC<Props> = ({ studentId, onChanged, readOnly = false }) => {
  const [linked, setLinked] = useState<Person[]>([]);
  const [suggested, setSuggested] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [working, setWorking] = useState<number | null>(null);
  const [options, setOptions] = useState<StudentLite[]>([]);
  const [query, setQuery] = useState('');
  const [picked, setPicked] = useState<StudentLite | null>(null);
  const [confirm, setConfirm] = useState<ConfirmRequest | null>(null);

  const load = useCallback(async () => {
    try {
      const siblings = await studentSiblingsAPI.getSiblings(studentId);
      setLinked(
        siblings.map((item: any) => ({
          id: item.sibling_info.id,
          name: item.sibling_info.full_name,
          admissionNumber: item.sibling_info.admission_number,
          className: item.sibling_info.class_name,
          dateOfBirth: item.sibling_info.date_of_birth,
        }))
      );
      setError(null);
    } catch (failure) {
      setError(apiError(failure));
    }
    if (!readOnly) {
      // Suggestions are a convenience; the list above still works without them
      try {
        const result = await studentSiblingsAPI.getSuggestions(studentId);
        setSuggested(
          (result.detected_siblings || []).map((item: any) => ({
            id: item.student_id,
            name: item.full_name,
            admissionNumber: item.admission_number,
            className: item.class_name,
            dateOfBirth: item.date_of_birth,
          }))
        );
      } catch {
        setSuggested([]);
      }
    }
    setLoading(false);
  }, [studentId, readOnly]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  // Search for any other student to link
  useEffect(() => {
    if (readOnly) return;
    let cancelled = false;
    const timer = setTimeout(() => {
      if (!query.trim()) {
        setOptions([]);
        return;
      }
      searchStudents({ search: query.trim(), per_page: 15 })
        .then((found) => !cancelled && setOptions(found.students))
        .catch(() => undefined);
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [query, readOnly]);

  const link = async (siblingId: number) => {
    setWorking(siblingId);
    setError(null);
    try {
      // The whole family changes: this student's siblings gain the new one, and the other way round
      const before = linked.map((person) => person.id);
      await studentSiblingsAPI.linkSibling(studentId, siblingId);
      setPicked(null);
      setQuery('');
      await load();
      onChanged?.([studentId, siblingId, ...before]);
    } catch (failure) {
      setError(apiError(failure));
    } finally {
      setWorking(null);
    }
  };

  const linkedIds = new Set([studentId, ...linked.map((person) => person.id)]);
  const choices = options.filter((option) => !linkedIds.has(option.id));

  if (loading) {
    return (
      <Box sx={{ py: 3, textAlign: 'center' }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <FamilyIcon sx={{ color: brand.violet }} />
        <Typography sx={{ fontWeight: 700 }}>
          Brothers and sisters at this school{' '}
          <Typography component="span" color="text.secondary">
            ({linked.length})
          </Typography>
        </Typography>
      </Box>
      {error && <Alert severity="error">{error}</Alert>}

      {linked.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          No siblings linked yet.{readOnly ? '' : ' Link them below so the sibling concession can count the family.'}
        </Typography>
      )}
      {linked.map((person) => (
        <PersonRow
          key={person.id}
          person={person}
          tone={brand.violet}
          action={
            !readOnly && (
              <Tooltip title="Not a sibling: remove the link">
                <IconButton
                  size="small"
                  color="error"
                  onClick={() =>
                    setConfirm({
                      title: 'Remove sibling',
                      message: `Remove ${person.name} from this family? ${person.name} loses the link to every sibling in it; the rest of the family stays linked.`,
                      confirmLabel: 'Remove',
                      danger: true,
                      onConfirm: async () => {
                        const family = linked.map((item) => item.id);
                        await studentSiblingsAPI.unlinkSibling(studentId, person.id);
                        await load();
                        onChanged?.([studentId, ...family]);
                      },
                    })
                  }
                >
                  <UnlinkIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            )
          }
        />
      ))}

      {!readOnly && suggested.length > 0 && (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Possibly siblings (same father’s name and phone). Link the ones that are right:
          </Typography>
          {suggested.map((person) => (
            <PersonRow
              key={person.id}
              person={person}
              tone="#f59e0b"
              action={
                <Button size="small" variant="contained" startIcon={<LinkIcon />} disabled={working !== null} onClick={() => link(person.id)}>
                  {working === person.id ? 'Linking…' : 'Link'}
                </Button>
              }
            />
          ))}
        </>
      )}

      {!readOnly && (
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start', mt: 1, flexWrap: 'wrap' }}>
          <Autocomplete
            sx={{ flexGrow: 1, minWidth: 240 }}
            size="small"
            options={choices}
            value={picked}
            inputValue={query}
            onChange={(_, value) => setPicked(value)}
            onInputChange={(_, value) => setQuery(value)}
            filterOptions={(items) => items}
            noOptionsText={query.trim() ? 'No student found' : 'Type a name or admission number'}
            getOptionLabel={(option) => `${option.first_name} ${option.last_name} (${option.admission_number})`}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            renderOption={(props, option) => (
              <li {...props} key={option.id}>
                <Box>
                  <Typography sx={{ fontSize: '0.9rem', fontWeight: 600 }}>
                    {option.first_name} {option.last_name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {[option.admission_number, option.class_name, option.father_name && `Father: ${option.father_name}`].filter(Boolean).join(' · ')}
                  </Typography>
                </Box>
              </li>
            )}
            renderInput={(params) => <TextField {...params} label="Link another student as a sibling" placeholder="Name or admission number" />}
          />
          <Button variant="contained" startIcon={<LinkIcon />} disabled={!picked || working !== null} onClick={() => picked && link(picked.id)} sx={{ height: 40 }}>
            Link
          </Button>
        </Box>
      )}
      <ConfirmDialog request={confirm} onClose={() => setConfirm(null)} />
    </Box>
  );
};

export default SiblingsManager;
