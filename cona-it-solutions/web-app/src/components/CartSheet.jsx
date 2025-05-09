import { useContext } from 'react'
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription, SheetClose } from "@/components/ui/sheet"
import CubCart from "./CubCart"
import { useState, useEffect } from "react"
import { Button } from './ui/button'
import { ShoppingCart } from 'lucide-react'
import Link from 'next/link'
import cubes from "@/db/cuburi.json"
import { CartContext } from '@/lib/context/cart'

export default function CartSheet() {
  const [side, setSide] = useState("top");
  const {cart, total} = useContext(CartContext);

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

  const cartCubes = cubes.filter((cube)=> cart.find((cartCube) => cartCube.cube_id == cube.id))

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
        {cartCubes.length ? 
        
          <div className="px-4 pb-4">
            <div className='flex flex-col my-8'>
              {cartCubes.map((cube, index)=>
                <CubCart cube={cube} key={index}/>
              )}
            </div>
            <p className='mb-8 text-xl'>Your order total is: <span className='font-bold'>{total.toFixed(2)} lei</span></p>
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

          :

          <div className='px-4 pb-4 text-center'>
            <p>No items in your cart</p>
            <SheetClose asChild>
              <Button asChild className="mt-5">
                <Link href="/products">Start shopping</Link>
              </Button>
            </SheetClose>
          </div>
        }
      </SheetContent>
    </Sheet>
  )
}
