import React from 'react';

interface IndiaFlagProps {
  size?: number;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Pixel-perfect, high-craft SVG representation of the Indian Tricolor flag (Tiranga).
 * Eliminates Windows-specific fallback to literal "IN" text for emoji 🇮🇳 while
 * providing crisp, retina-sharp display across all platforms.
 */
export const IndiaFlag: React.FC<IndiaFlagProps> = ({
  size = 16,
  className = '',
  style,
}) => {
  const width = size;
  const height = Math.max(10, Math.round((size * 2) / 3));

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 900 600"
      className={`india-flag-svg ${className}`}
      style={{
        display: 'inline-block',
        verticalAlign: 'middle',
        borderRadius: '2px',
        boxShadow: '0 0 0 1px rgba(15, 23, 42, 0.12)',
        flexShrink: 0,
        ...style,
      }}
      role="img"
      aria-label="India flag"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Saffron Top Band */}
      <rect width="900" height="200" fill="#FF9933" />
      {/* White Middle Band */}
      <rect y="200" width="900" height="200" fill="#FFFFFF" />
      {/* Green Bottom Band */}
      <rect y="400" width="900" height="200" fill="#138808" />

      {/* Ashoka Chakra in Navy Blue */}
      <g transform="translate(450, 300)">
        <circle r="78" fill="none" stroke="#000080" strokeWidth="15" />
        <circle r="18" fill="#000080" />
        {/* 24 Spokes (15 deg separation) */}
        {Array.from({ length: 24 }).map((_, i) => (
          <line
            key={i}
            x1="0"
            y1="0"
            x2="0"
            y2="-78"
            stroke="#000080"
            strokeWidth="5.5"
            transform={`rotate(${i * 15})`}
          />
        ))}
      </g>
    </svg>
  );
};

export default IndiaFlag;
