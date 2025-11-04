// Tron-inspired global styles
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
