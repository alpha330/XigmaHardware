'use client';
import { useState } from 'react';
import styled from '@emotion/styled';

const Gallery = styled.div`
  .main { width: 100%; height: 400px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; border-radius: 12px; margin-bottom: 16px; font-size: 6rem; }
  .thumbs { display: flex; gap: 8px; }
  .thumb { width: 72px; height: 72px; background: #f1f5f9; border-radius: 8px; cursor: pointer; border: 2px solid transparent; display: flex; align-items: center; justify-content: center; font-size: 2rem; }
  .thumb.active { border-color: #8b5cf6; }
`;

export const ProductGallery = ({ media }) => (
  <Gallery>
    <div className="main">{media[0]?.image ? <img src={media[0].image} alt="" /> : '🖥️'}</div>
    <div className="thumbs">
      {media.map((m, i) => (
        <div key={i} className={`thumb ${i === 0 ? 'active' : ''}`}>
          {m.image ? <img src={m.image} alt="" /> : '🖼️'}
        </div>
      ))}
    </div>
  </Gallery>
);