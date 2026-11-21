import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { PwaRegister } from "@/components/PwaRegister";

export const metadata: Metadata = {
  title: "RubbleEar", description: "Offline acoustic survivor detection", manifest: "/manifest.webmanifest",
};
export const viewport: Viewport = { themeColor: "#b3261e", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif", background: "#0b0b0b", color: "#eee" }}>
        <PwaRegister />{children}
      </body>
    </html>
  );
}
