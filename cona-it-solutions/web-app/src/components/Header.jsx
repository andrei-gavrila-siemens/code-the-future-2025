"use client"

import Link from "next/link"
import { Cuboid } from "lucide-react"
import { Button } from "@/components/ui/button"
import CartSheet from "./CartSheet"

export default function Header() {

  return (
    <nav className="w-full border-b sticky top-0 bg-white">
      <div className="flex items-center justify-between px-8 py-5">
        <Link href="/" className="flex items-center">
          <Cuboid />
          <span className="text-xl font-bold ms-2">CUBURI</span>
        </Link>

        <div className="flex items-center gap-2">
          <Button asChild variant="ghost">
            <Link href="/products" aria-label="View products">
              Products
            </Link>
          </Button>

          <CartSheet />
        </div>
      </div>
    </nav>
  )
}

