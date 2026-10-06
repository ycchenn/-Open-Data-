"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/record", label: "🎙️ 說農事" },
  { href: "/logs", label: "📒 農事日誌" },
  { href: "/marketing", label: "✍️ 行銷文案" },
  { href: "/qa", label: "💬 農業問答" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="nav">
      <Link href="/" className="brand">🌱 農情 AI 語</Link>
      {LINKS.map((l) => (
        <Link key={l.href} href={l.href} className={pathname.startsWith(l.href) ? "active" : ""}>
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
