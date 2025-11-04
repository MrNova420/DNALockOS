// Global Tron-Inspired CSS with Animations
export default function GlobalStyles() {
  return (
    <style jsx global>{`
      @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap');

      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
      }

      body {
        font-family: 'Orbitron', 'Rajdhani', monospace;
        background: #000;
        color: #00ffff;
        overflow-x: hidden;
        cursor: crosshair;
      }

      /* Tron Grid Animation */
      @keyframes gridScroll {
        0% {
          transform: translateY(0);
        }
        100% {
          transform: translateY(50px);
        }
      }

      /* Glow Pulse Animation */
      @keyframes pulse {
        0%, 100% {
          transform: scale(1);
          filter: drop-shadow(0 0 10px #00ffff);
        }
        50% {
          transform: scale(1.05);
          filter: drop-shadow(0 0 20px #00ffff) drop-shadow(0 0 40px #00ffff);
        }
      }

      /* Text Glow */
      @keyframes textGlow {
        0%, 100% {
          text-shadow: 
            0 0 10px #00ffff,
            0 0 20px #00ffff,
            0 0 30px #00ffff;
        }
        50% {
          text-shadow: 
            0 0 20px #00ffff,
            0 0 40px #00ffff,
            0 0 60px #00ffff,
            0 0 80px #00ffff;
        }
      }

      /* Border Glow Animation */
      @keyframes borderGlow {
        0%, 100% {
          box-shadow: 
            0 0 10px rgba(0, 255, 255, 0.5),
            inset 0 0 10px rgba(0, 255, 255, 0.1);
        }
        50% {
          box-shadow: 
            0 0 20px rgba(0, 255, 255, 0.8),
            0 0 40px rgba(0, 255, 255, 0.6),
            inset 0 0 20px rgba(0, 255, 255, 0.2);
        }
      }

      /* Scan Line Effect */
      @keyframes scanline {
        0% {
          transform: translateY(-100%);
        }
        100% {
          transform: translateY(100vh);
        }
      }

      /* Particle Float */
      @keyframes particleFloat {
        0%, 100% {
          transform: translateY(0) translateX(0);
        }
        25% {
          transform: translateY(-20px) translateX(10px);
        }
        50% {
          transform: translateY(-10px) translateX(-10px);
        }
        75% {
          transform: translateY(-15px) translateX(5px);
        }
      }

      /* Rotate */
      @keyframes rotate {
        from {
          transform: rotate(0deg);
        }
        to {
          transform: rotate(360deg);
        }
      }

      /* Fade In */
      @keyframes fadeIn {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      /* Slide In from Left */
      @keyframes slideInLeft {
        from {
          opacity: 0;
          transform: translateX(-50px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      /* Slide In from Right */
      @keyframes slideInRight {
        from {
          opacity: 0;
          transform: translateX(50px);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      /* Scanline Effect Overlay */
      body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(
          to bottom,
          transparent,
          rgba(0, 255, 255, 0.5),
          transparent
        );
        animation: scanline 8s linear infinite;
        pointer-events: none;
        z-index: 9999;
      }

      /* Custom Scrollbar */
      ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
      }

      ::-webkit-scrollbar-track {
        background: #000;
        border-left: 2px solid #00ffff;
      }

      ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ffff 0%, #00cccc 100%);
        border-radius: 6px;
        border: 2px solid #000;
      }

      ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00ffff 0%, #00aaaa 100%);
        box-shadow: 0 0 10px #00ffff;
      }

      /* Selection */
      ::selection {
        background: rgba(0, 255, 255, 0.3);
        color: #00ffff;
        text-shadow: 0 0 10px #00ffff;
      }

      /* Input Styles */
      input:focus,
      textarea:focus,
      select:focus {
        outline: none;
        border-color: #00ffff;
        box-shadow: 
          0 0 20px rgba(0, 255, 255, 0.5),
          inset 0 0 10px rgba(0, 255, 255, 0.2);
        animation: borderGlow 2s ease-in-out infinite;
      }

      input:focus::placeholder {
        color: transparent;
      }

      /* Button Hover Effects */
      button:hover:not(:disabled) {
        transform: scale(1.05) translateY(-2px);
        box-shadow: 
          0 0 30px rgba(0, 255, 255, 0.7),
          0 5px 15px rgba(0, 255, 255, 0.4);
        animation: pulse 1s ease-in-out infinite;
      }

      button:active:not(:disabled) {
        transform: scale(0.98);
      }

      button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        filter: grayscale(0.5);
      }

      /* Table Styles */
      table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
      }

      table th {
        background: rgba(0, 255, 255, 0.1);
        border: 2px solid #00ffff;
        padding: 15px;
        text-align: left;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: bold;
        position: sticky;
        top: 0;
        z-index: 10;
      }

      table td {
        border: 1px solid rgba(0, 255, 255, 0.3);
        padding: 12px;
        transition: all 0.3s;
      }

      table tr:hover td {
        background: rgba(0, 255, 255, 0.05);
        border-color: #00ffff;
      }

      /* Link Styles */
      a {
        color: #00ffff;
        text-decoration: none;
        transition: all 0.3s;
        position: relative;
      }

      a::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: #00ffff;
        transition: width 0.3s;
      }

      a:hover {
        text-shadow: 0 0 10px #00ffff;
      }

      a:hover::after {
        width: 100%;
        box-shadow: 0 0 10px #00ffff;
      }

      /* Card Hover Effect */
      .card {
        transition: all 0.3s;
      }

      .card:hover {
        transform: translateY(-5px);
        box-shadow: 
          0 10px 30px rgba(0, 255, 255, 0.3),
          0 0 50px rgba(0, 255, 255, 0.2);
      }

      /* Loading Animation */
      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }

      .loading {
        border: 3px solid rgba(0, 255, 255, 0.3);
        border-top-color: #00ffff;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
      }

      /* Tooltip */
      [data-tooltip] {
        position: relative;
        cursor: help;
      }

      [data-tooltip]::before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 8px 12px;
        background: rgba(0, 0, 0, 0.9);
        border: 2px solid #00ffff;
        border-radius: 5px;
        font-size: 12px;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.3s;
        z-index: 1000;
      }

      [data-tooltip]:hover::before {
        opacity: 1;
      }

      /* Responsive */
      @media (max-width: 768px) {
        body {
          font-size: 14px;
        }

        h1 {
          font-size: 32px !important;
        }

        h2 {
          font-size: 24px !important;
        }
      }

      /* Print Styles */
      @media print {
        body::before {
          display: none;
        }

        * {
          color: #000 !important;
          background: #fff !important;
        }
      }
    `}</style>
  );
}
