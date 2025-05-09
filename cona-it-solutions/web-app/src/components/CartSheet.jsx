import React from 'react'
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription, SheetClose } from "@/components/ui/sheet"
import CubCart from "./CubCart"
import { useState, useEffect } from "react"
import { Button } from './ui/button'
import { ShoppingCart } from 'lucide-react'
import Link from 'next/link'

export default function CartSheet() {
  const [side, setSide] = useState("top");

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 650) {
        setSide("right");
      } else {
        setSide("top");
      }
    };

    // Run once on mount
    handleResize();

    // Add event listener
    window.addEventListener("resize", handleResize);

    // Cleanup
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <ShoppingCart />
        </Button>
      </SheetTrigger>
      <SheetContent side={side}>
        <SheetHeader>
          <SheetTitle className="text-2xl">
            My cart
          </SheetTitle>
          <SheetDescription>
          </SheetDescription>
        </SheetHeader>
        <div className="px-4 pb-4">
          <div className='flex flex-col my-8'>
            <CubCart />
            <CubCart />
            <CubCart />
          </div>
          <p className='mb-8 text-xl'>Your order total is: <span className='font-bold'>30.00 lei</span></p>
          <SheetClose asChild>
            <Button asChild>
              <Link href="/confirmation">
                Confirm order
              </Link>
            </Button>
          </SheetClose>
          <SheetClose asChild>
            <Button variant="secondary" className="ms-2" asChild>
              <Link href="/products">
                Shop for more
              </Link>
            </Button>
          </SheetClose>
        </div>
      </SheetContent>
    </Sheet>
  )
}
