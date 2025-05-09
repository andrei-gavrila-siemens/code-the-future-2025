"use client"

import Link from "next/link"
import { ShoppingCart, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription, SheetClose } from "@/components/ui/sheet"

export default function Header() {

  return (
    <nav className="w-full border-b">
      <div className="flex items-center justify-between px-8 py-5">
        <Link href="/" className="flex items-center">
          <span className="text-xl font-bold">CUBURI</span>
        </Link>

        <div className="flex items-center gap-2">
          <Link href="/cart" aria-label="Shopping cart">
            <Button variant="ghost" size="icon" className="relative">
              <ShoppingCart className="h-5 w-5" />
            </Button>
          </Link>

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Menu />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>
                  Discover what CUBURI has to offer
                </SheetTitle>
                <SheetDescription>
                  <SheetClose asChild>
                    <Link href={"/products"}>
                      Search Products
                    </Link>
                  </SheetClose>
                </SheetDescription>
              </SheetHeader>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </nav>
  )
}

