import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ShivvayOS Dashboard",
  description: "Workflow monitoring dashboard for ShivvayOS.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-slate-50">
          <main className="mx-auto max-w-7xl p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
