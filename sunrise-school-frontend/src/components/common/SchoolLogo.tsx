import React, { useState } from 'react';
import { Box } from '@mui/material';
import { useSchool } from '../../contexts/SchoolContext';
import { brand, ease } from '../../theme';

interface SchoolLogoProps {
  size?: number;
  /** Gradient ring around the logo (used on dark backgrounds). */
  ring?: boolean;
}

/** The school's logo, or its initial on a gradient tile when it has none. */
const SchoolLogo: React.FC<SchoolLogoProps> = ({ size = 44, ring = false }) => {
  const { school } = useSchool();
  const [broken, setBroken] = useState(false);
  const radius = Math.round(size * 0.3);
  const showImage = school.logoUrl && !broken;

  return (
    <Box
      sx={{
        width: size,
        height: size,
        flexShrink: 0,
        borderRadius: `${radius}px`,
        p: ring ? '3px' : 0,
        background: ring ? 'linear-gradient(135deg, #60a5fa, #a78bfa 55%, #f472b6)' : 'transparent',
        boxShadow: ring ? '0 10px 26px rgba(59,130,246,0.45)' : 'none',
        transition: `transform 0.5s ${ease}`,
        '&:hover': { transform: 'rotate(-6deg) scale(1.06)' },
      }}
    >
      {showImage ? (
        <Box
          component="img"
          src={school.logoUrl!}
          alt={`${school.shortName} logo`}
          onError={() => setBroken(true)}
          sx={{ display: 'block', width: '100%', height: '100%', objectFit: 'cover', borderRadius: `${radius - (ring ? 3 : 0)}px`, background: '#fff' }}
        />
      ) : (
        <Box
          aria-label={`${school.shortName} logo`}
          sx={{
            display: 'grid',
            placeItems: 'center',
            width: '100%',
            height: '100%',
            borderRadius: `${radius - (ring ? 3 : 0)}px`,
            color: '#fff',
            fontWeight: 800,
            fontSize: size * 0.45,
            background: brand.gradient,
          }}
        >
          {school.shortName.charAt(0).toUpperCase()}
        </Box>
      )}
    </Box>
  );
};

export default SchoolLogo;
