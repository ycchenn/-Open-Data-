import type { Metadata } from "next";
import Nav from "@/components/Nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "農情 AI 語",
  description: "結合 Open Data 的智慧農務與品牌文案生成助手",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-Hant-TW">
      <body>
        <Nav />
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
