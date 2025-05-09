"use client"

import { createContext } from "react";
import {useCart} from "@/lib/hooks/cart.js";

export const CartContext = createContext()

export function CartProvider({children}) {

  const cart = useCart();

  return (
    <CartContext.Provider value={cart}>
      {children}
    </CartContext.Provider>
  )
}