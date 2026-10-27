import type { Metadata } from "next";
import { Toaster } from "sonner";
// Polices auto-hébergées via npm : aucun appel à Google Fonts à l'exécution.
import "@fontsource/ibm-plex-sans/400.css";
import "@fontsource/ibm-plex-sans/500.css";
import "@fontsource/ibm-plex-sans/600.css";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "AirLiquide GMAO+",
  description: "Suivi SAV et maintenance des dispositifs médicaux",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {children}
        <Toaster position="bottom-right" closeButton />
      </body>
    </html>
  );
}
