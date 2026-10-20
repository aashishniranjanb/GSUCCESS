import React from "react";

export function BotanicalHeroGraphic({ className = "" }: { className?: string }) {
  return (
    <div className={`relative overflow-hidden pointer-events-none select-none ${className}`} aria-hidden="true">
      <svg
        viewBox="0 0 520 220"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full object-contain"
      >
        <defs>
          <linearGradient id="leafGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ADE80" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#15803D" stopOpacity="0.4" />
          </linearGradient>
          <linearGradient id="leafGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#86EFAC" stopOpacity="0.7" />
            <stop offset="100%" stopColor="#166534" stopOpacity="0.25" />
          </linearGradient>
          <linearGradient id="chemGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#1E3A8A" stopOpacity="0.1" />
          </linearGradient>
          <linearGradient id="amberGlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FBBF24" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#B45309" stopOpacity="0.15" />
          </linearGradient>
          <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Ambient atmospheric backdrop glow */}
        <circle cx="280" cy="110" r="90" fill="#22C55E" opacity="0.08" filter="url(#glowFilter)" />
        <circle cx="420" cy="80" r="70" fill="#3B82F6" opacity="0.07" filter="url(#glowFilter)" />

        {/* Chemical ring nodes (Benzene/Receptor skeleton) */}
        <g stroke="#60A5FA" strokeWidth="1.2" opacity="0.35" strokeDasharray="3 3">
          <polygon points="400,60 425,75 425,105 400,120 375,105 375,75" />
          <line x1="425" y1="75" x2="445" y2="65" />
          <circle cx="445" cy="65" r="2.5" fill="#60A5FA" />
          <line x1="400" y1="120" x2="400" y2="140" />
          <circle cx="400" cy="140" r="2" fill="#93C5FD" />
        </g>

        {/* Flowing Organic Botanical Leaves - Left Stalk */}
        <g className="animate-sway origin-bottom-left">
          {/* Main stem curve */}
          <path
            d="M 60 220 Q 110 140 160 80"
            stroke="#22C55E"
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.6"
          />
          {/* Leaf 1 */}
          <path
            d="M 120 150 C 90 125 100 95 140 115 C 130 135 125 145 120 150 Z"
            fill="url(#leafGrad1)"
          />
          {/* Leaf 2 */}
          <path
            d="M 140 110 C 165 80 195 90 180 125 C 160 120 145 115 140 110 Z"
            fill="url(#leafGrad2)"
          />
          {/* Leaf 3 (Top sprout) */}
          <path
            d="M 160 80 C 175 45 200 55 190 85 C 175 85 165 82 160 80 Z"
            fill="url(#leafGrad1)"
          />
        </g>

        {/* Central Student Scholar Silhouette & Open Pharmacopeia */}
        <g opacity="0.95">
          {/* Desk / Bench base line */}
          <line x1="160" y1="195" x2="380" y2="195" stroke="#334155" strokeWidth="2" strokeLinecap="round" />

          {/* Stacked Textbook Spines with Subject Color Codes */}
          <g>
            {/* Book 1 - Pharmacology (Forest Green) */}
            <rect x="180" y="178" width="85" height="15" rx="2" fill="#14532D" stroke="#22C55E" strokeWidth="1" />
            <text x="188" y="189" fill="#86EFAC" fontSize="8" fontFamily="var(--font-mono)" fontWeight="bold">PHARMACOLOGY</text>

            {/* Book 2 - Pharmaceutics (Sky Blue) */}
            <rect x="184" y="161" width="82" height="15" rx="2" fill="#1E3A8A" stroke="#3B82F6" strokeWidth="1" />
            <text x="192" y="172" fill="#93C5FD" fontSize="8" fontFamily="var(--font-mono)" fontWeight="bold">PHARMACEUTICS</text>

            {/* Book 3 - Chemistry (Amber) */}
            <rect x="188" y="144" width="76" height="15" rx="2" fill="#78350F" stroke="#F59E0B" strokeWidth="1" />
            <text x="196" y="155" fill="#FDE047" fontSize="8" fontFamily="var(--font-mono)" fontWeight="bold">BIOCHEMISTRY</text>
          </g>

          {/* Open Studying Codex / Laptop */}
          <path
            d="M 285 170 L 320 188 L 355 170 L 355 190 L 320 205 L 285 190 Z"
            fill="#1E293B"
            stroke="#64748B"
            strokeWidth="1.2"
          />
          <line x1="320" y1="188" x2="320" y2="205" stroke="#475569" strokeWidth="1.2" />

          {/* Focus Light Beam over open book */}
          <polygon points="320,130 290,185 350,185" fill="#60A5FA" opacity="0.08" />

          {/* Stylized Aspirant Silhouette (Head & Lab Coat Shoulders) */}
          {/* Hair & head */}
          <path
            d="M 310 115 C 310 98 330 98 330 115 C 330 126 310 126 310 115 Z"
            fill="#334155"
          />
          {/* Face highlight */}
          <circle cx="320" cy="115" r="7" fill="#F8FAFC" opacity="0.9" />
          {/* Hair flow */}
          <path
            d="M 312 108 C 302 115 304 135 308 142 C 314 130 316 115 318 108 Z"
            fill="#1E293B"
          />
          {/* Lab coat shoulders & collar */}
          <path
            d="M 302 145 C 302 135 338 135 338 145 L 348 180 L 292 180 Z"
            fill="#F1F5F9"
            opacity="0.88"
          />
          {/* Green stethoscope / ribbon collar */}
          <path
            d="M 312 142 Q 320 156 328 142"
            stroke="#22C55E"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
          />
        </g>

        {/* Right Botanical Branch */}
        <g className="animate-sway origin-bottom-right" style={{ animationDelay: "-2.5s" }}>
          <path
            d="M 470 210 Q 450 130 420 70"
            stroke="#15803D"
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.55"
          />
          <path
            d="M 435 110 C 465 95 480 120 455 130 C 445 125 438 118 435 110 Z"
            fill="url(#leafGrad2)"
          />
          <path
            d="M 425 75 C 445 45 465 60 445 80 Z"
            fill="url(#leafGrad1)"
          />
        </g>

        {/* Glowing floating knowledge spores (Particles) */}
        <circle cx="160" cy="65" r="3" fill="#86EFAC" className="animate-pulse-soft" />
        <circle cx="380" cy="45" r="2.5" fill="#93C5FD" className="animate-pulse-soft" style={{ animationDelay: "-1s" }} />
        <circle cx="465" cy="140" r="2" fill="#FDE047" className="animate-pulse-soft" style={{ animationDelay: "-2s" }} />
        <circle cx="240" cy="80" r="1.5" fill="#86EFAC" opacity="0.6" />
      </svg>
    </div>
  );
}

export function SynapseIllustration({ className = "" }: { className?: string }) {
  return (
    <div className={`pointer-events-none select-none ${className}`} aria-hidden="true">
      <svg viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        <defs>
          <linearGradient id="synapseGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ADE80" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#166534" stopOpacity="0.3" />
          </linearGradient>
          <filter id="neuroGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Presynaptic Terminal bulb */}
        <path
          d="M 40 20 C 40 60 70 85 80 85 C 90 85 120 60 120 20 Z"
          fill="url(#synapseGrad)"
          stroke="#4ADE80"
          strokeWidth="1.5"
          opacity="0.85"
        />

        {/* Postsynaptic membrane */}
        <path
          d="M 30 135 C 60 115 100 115 130 135"
          stroke="#22C55E"
          strokeWidth="3"
          strokeLinecap="round"
          opacity="0.7"
        />

        {/* Receptor cups */}
        <path d="M 55 124 C 55 129 65 129 65 124" stroke="#86EFAC" strokeWidth="2" fill="none" />
        <path d="M 75 122 C 75 127 85 127 85 122" stroke="#86EFAC" strokeWidth="2" fill="none" />
        <path d="M 95 124 C 95 129 105 129 105 124" stroke="#86EFAC" strokeWidth="2" fill="none" />

        {/* Neurotransmitter vesicles and released quanta */}
        <circle cx="80" cy="55" r="4.5" fill="#FCD34D" filter="url(#neuroGlow)" className="animate-pulse-soft" />
        <circle cx="65" cy="45" r="4" fill="#FBBF24" opacity="0.8" />
        <circle cx="95" cy="48" r="4" fill="#FBBF24" opacity="0.8" />

        {/* Released transmitters floating across cleft */}
        <circle cx="60" cy="100" r="3" fill="#FDE047" className="animate-pulse-soft" style={{ animationDelay: "-0.5s" }} />
        <circle cx="80" cy="106" r="3.5" fill="#4ADE80" filter="url(#neuroGlow)" className="animate-pulse-soft" />
        <circle cx="100" cy="98" r="3" fill="#FDE047" className="animate-pulse-soft" style={{ animationDelay: "-1.5s" }} />
      </svg>
    </div>
  );
}

export function DissolutionIllustration({ className = "" }: { className?: string }) {
  return (
    <div className={`pointer-events-none select-none ${className}`} aria-hidden="true">
      <svg viewBox="0 0 160 160" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        <defs>
          <linearGradient id="beakerFluid" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#1E3A8A" stopOpacity="0.75" />
          </linearGradient>
          <linearGradient id="tabletGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#93C5FD" stopOpacity="0.7" />
          </linearGradient>
          <filter id="fluidGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Laboratory Beaker Outline */}
        <path
          d="M 35 30 L 35 125 C 35 138 45 145 60 145 L 100 145 C 115 145 125 138 125 125 L 125 30"
          stroke="#94A3B8"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.65"
        />
        {/* Beaker lip */}
        <line x1="30" y1="30" x2="40" y2="30" stroke="#94A3B8" strokeWidth="2" strokeLinecap="round" />
        <line x1="120" y1="30" x2="130" y2="30" stroke="#94A3B8" strokeWidth="2" strokeLinecap="round" />

        {/* Dissolution Fluid meniscus & volume */}
        <path
          d="M 37 65 Q 80 58 123 65 L 123 125 C 123 136 113 143 100 143 L 60 143 C 47 143 37 136 37 125 Z"
          fill="url(#beakerFluid)"
        />

        {/* Graduated volume markings */}
        <line x1="110" y1="80" x2="120" y2="80" stroke="#CBD5E1" strokeWidth="1.2" opacity="0.5" />
        <line x1="105" y1="95" x2="120" y2="95" stroke="#CBD5E1" strokeWidth="1.2" opacity="0.5" />
        <line x1="110" y1="110" x2="120" y2="110" stroke="#CBD5E1" strokeWidth="1.2" opacity="0.5" />

        {/* Compressed Tablet sinking / dissolving */}
        <g transform="translate(62, 95) rotate(-15)">
          <ellipse cx="18" cy="12" rx="16" ry="10" fill="url(#tabletGrad)" stroke="#60A5FA" strokeWidth="1" />
          <line x1="8" y1="12" x2="28" y2="12" stroke="#3B82F6" strokeWidth="1" opacity="0.5" />
        </g>

        {/* Diffusion boundary layer particles (Noyes-Whitney model) */}
        <circle cx="85" cy="88" r="2.5" fill="#93C5FD" className="animate-pulse-soft" />
        <circle cx="95" cy="78" r="2" fill="#BAE6FD" className="animate-pulse-soft" style={{ animationDelay: "-0.8s" }} />
        <circle cx="68" cy="80" r="2" fill="#E0F2FE" className="animate-pulse-soft" style={{ animationDelay: "-1.6s" }} />
        <circle cx="58" cy="90" r="1.5" fill="#93C5FD" opacity="0.7" />
        <circle cx="92" cy="105" r="1.8" fill="#BAE6FD" opacity="0.8" />
      </svg>
    </div>
  );
}
