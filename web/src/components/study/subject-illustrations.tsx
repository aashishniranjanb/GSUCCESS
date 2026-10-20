import React from "react";

export function ChemistryMolecularIllustration({ className = "" }: { className?: string }) {
  return (
    <div className={`pointer-events-none select-none ${className}`} aria-hidden="true">
      <svg viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        <defs>
          <linearGradient id="amberBall" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FDE047" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#D97706" stopOpacity="0.8" />
          </linearGradient>
        </defs>
        {/* Bonds */}
        <line x1="80" y1="80" x2="115" y2="55" stroke="#FBBF24" strokeWidth="2.5" opacity="0.6" />
        <line x1="80" y1="80" x2="45" y2="55" stroke="#FBBF24" strokeWidth="2.5" opacity="0.6" />
        <line x1="80" y1="80" x2="80" y2="120" stroke="#FBBF24" strokeWidth="2.5" opacity="0.6" />
        <line x1="115" y1="55" x2="135" y2="85" stroke="#F59E0B" strokeWidth="2" opacity="0.4" strokeDasharray="3 3" />
        <line x1="45" y1="55" x2="25" y2="85" stroke="#F59E0B" strokeWidth="2" opacity="0.4" strokeDasharray="3 3" />

        {/* Central Core Atom */}
        <circle cx="80" cy="80" r="14" fill="url(#amberBall)" stroke="#FBBF24" strokeWidth="1.5" />
        {/* Orbital Atoms */}
        <circle cx="115" cy="55" r="9" fill="url(#amberBall)" stroke="#FBBF24" strokeWidth="1" />
        <circle cx="45" cy="55" r="9" fill="url(#amberBall)" stroke="#FBBF24" strokeWidth="1" />
        <circle cx="80" cy="120" r="11" fill="url(#amberBall)" stroke="#FBBF24" strokeWidth="1" />
        <circle cx="135" cy="85" r="6" fill="#FDE047" opacity="0.7" />
        <circle cx="25" cy="85" r="6" fill="#FDE047" opacity="0.7" />
      </svg>
    </div>
  );
}

export function PharmacognosyFlowerIllustration({ className = "" }: { className?: string }) {
  return (
    <div className={`pointer-events-none select-none ${className}`} aria-hidden="true">
      <svg viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        <defs>
          <linearGradient id="petalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#E9D5FF" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#7E22CE" stopOpacity="0.7" />
          </linearGradient>
          <linearGradient id="mortarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#A855F7" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#3B0764" stopOpacity="0.8" />
          </linearGradient>
        </defs>
        {/* Botanical Petals */}
        <ellipse cx="80" cy="55" rx="14" ry="24" fill="url(#petalGrad)" />
        <ellipse cx="102" cy="70" rx="14" ry="24" transform="rotate(45 102 70)" fill="url(#petalGrad)" opacity="0.85" />
        <ellipse cx="58" cy="70" rx="14" ry="24" transform="rotate(-45 58 70)" fill="url(#petalGrad)" opacity="0.85" />
        <circle cx="80" cy="75" r="9" fill="#FDE047" opacity="0.9" />

        {/* Mortar & Pestle outline */}
        <path d="M 45 110 C 45 135 115 135 115 110 Z" fill="url(#mortarGrad)" stroke="#C084FC" strokeWidth="1.5" />
        <line x1="68" y1="85" x2="88" y2="115" stroke="#E9D5FF" strokeWidth="3.5" strokeLinecap="round" />
      </svg>
    </div>
  );
}

export function BiotechnologyDnaIllustration({ className = "" }: { className?: string }) {
  return (
    <div className={`pointer-events-none select-none ${className}`} aria-hidden="true">
      <svg viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        <defs>
          <linearGradient id="dnaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2DD4BF" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#0F766E" stopOpacity="0.7" />
          </linearGradient>
        </defs>
        {/* Double Helix rungs */}
        <line x1="55" y1="40" x2="105" y2="40" stroke="#5EEAD4" strokeWidth="2" opacity="0.6" />
        <line x1="62" y1="60" x2="98" y2="60" stroke="#5EEAD4" strokeWidth="2" opacity="0.6" />
        <line x1="72" y1="80" x2="88" y2="80" stroke="#5EEAD4" strokeWidth="2" opacity="0.6" />
        <line x1="62" y1="100" x2="98" y2="100" stroke="#5EEAD4" strokeWidth="2" opacity="0.6" />
        <line x1="55" y1="120" x2="105" y2="120" stroke="#5EEAD4" strokeWidth="2" opacity="0.6" />

        {/* Helix strands */}
        <path d="M 55 30 Q 75 75 55 125" stroke="url(#dnaGrad)" strokeWidth="3" strokeLinecap="round" fill="none" />
        <path d="M 105 30 Q 85 75 105 125" stroke="url(#dnaGrad)" strokeWidth="3" strokeLinecap="round" fill="none" />

        <circle cx="55" cy="40" r="3.5" fill="#5EEAD4" />
        <circle cx="105" cy="40" r="3.5" fill="#2DD4BF" />
        <circle cx="72" cy="80" r="3" fill="#99F6E4" />
        <circle cx="88" cy="80" r="3" fill="#99F6E4" />
        <circle cx="55" cy="120" r="3.5" fill="#5EEAD4" />
        <circle cx="105" cy="120" r="3.5" fill="#2DD4BF" />
      </svg>
    </div>
  );
}
