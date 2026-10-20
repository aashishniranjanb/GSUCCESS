import type { Metadata, Viewport } from "next";
import { Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layout/app-shell";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "GPAT 2027 Learning OS",
    template: "%s — GPAT 2027",
  },
  description:
    "Adaptive learning, active recall, and spaced repetition for GPAT 2027 preparation.",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#0C0E14",
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${jakarta.variable} ${jetbrains.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var p = localStorage.getItem('gpat_learning_os_preferences');
                  var theme = p ? JSON.parse(p).theme : 'dark';
                  if (theme) {
                    document.documentElement.setAttribute('data-theme', theme);
                    if (theme === 'light' || theme === 'warm-editorial') {
                      document.documentElement.classList.add('light');
                    } else {
                      document.documentElement.classList.add('dark');
                    }
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="bg-[var(--color-bg-base)] text-[var(--color-text-primary)] antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
