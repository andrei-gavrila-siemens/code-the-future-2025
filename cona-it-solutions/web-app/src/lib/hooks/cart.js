'use client';

import { useState } from "react";

export const useCart = ()=>{
  const [cart, setCart] = useState([]);

  function addToCart(id, price_unit) {
    setCart((prev) => {
      const existingCube = prev.find((item) => item.cube_id === id);
  
      if (existingCube) {
        // Update quantity for the existing cube
        return prev.map((item) =>
          item.cube_id === id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        // Add new cube to cart
        return [...prev, { cube_id: id, quantity: 1, price_unit: price_unit }];
      }
    });
  }

  function increaseQuantity(id){
    setCart((prev)=>
      prev.map((item) =>
        item.cube_id === id
          ? { ...item, quantity: item.quantity + 1 }
          : item
    ))
  }

  function decrementQuanity(id){
    setCart((prev)=>
      prev.map((item) =>
        item.cube_id === id
          ? { ...item, quantity: item.quantity - 1 }
          : item
    ))
  }

  return {cart, setCart, addToCart, increaseQuantity, decrementQuanity};
}