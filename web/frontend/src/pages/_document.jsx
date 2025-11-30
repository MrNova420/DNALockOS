/**
 * =============================================================================
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * =============================================================================
 *
 * OWNERSHIP AND LEGAL NOTICE:
 *
 * This software and all associated intellectual property is the exclusive
 * property of WeNova Interactive, legally owned and operated by:
 *
 *     Kayden Shawn Massengill
 *
 * COMMERCIAL SOFTWARE - NOT FREE - NOT OPEN SOURCE
 *
 * This is proprietary commercial software. It is NOT free software. It is NOT
 * open source software. This software is developed for commercial sale and
 * requires a valid commercial license for ANY use.
 *
 * STRICT PROHIBITION NOTICE:
 *
 * Without a valid commercial license agreement, you are PROHIBITED from:
 *   - Using this software for any purpose
 *   - Copying, reproducing, or duplicating this software
 *   - Modifying, adapting, or creating derivative works
 *   - Distributing, publishing, or transferring this software
 *   - Reverse engineering, decompiling, or disassembling this software
 *   - Sublicensing or permitting any third-party access
 *
 * LEGAL ENFORCEMENT:
 *
 * Unauthorized use will be prosecuted to the maximum extent of applicable law.
 *
 * For licensing inquiries: WeNova Interactive
 * =============================================================================
 */

/**
 * DNALockOS - DNA-Key Authentication System
 * Copyright (c) 2025 WeNova Interactive
 * Legal Owner: Kayden Shawn Massengill
 * ALL RIGHTS RESERVED.
 *
 * PROPRIETARY AND CONFIDENTIAL
 * This is commercial software. Unauthorized copying, modification,
 * distribution, or use is strictly prohibited.
 */

// DNA-inspired global styles
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html>
      <Head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet" />
      </Head>
      <body>
        <Main />
        <NextScript />
        <style jsx global>{`
          * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
          }
          
          body {
            font-family: 'Orbitron', monospace;
            background: #000;
            color: #00ffff;
            overflow-x: hidden;
          }

          @keyframes glow {
            0%, 100% {
              text-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff;
            }
            50% {
              text-shadow: 0 0 30px #00ffff, 0 0 60px #00ffff;
            }
          }

          table th {
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid #00ffff;
            padding: 15px;
            text-align: left;
            text-transform: uppercase;
            letter-spacing: 1px;
          }

          table td {
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 12px;
          }

          table tr:hover {
            background: rgba(0, 255, 255, 0.05);
          }

          button:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.7);
          }

          button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
          }

          input:focus {
            outline: none;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
          }
        `}</style>
      </body>
    </Html>
  );
}
