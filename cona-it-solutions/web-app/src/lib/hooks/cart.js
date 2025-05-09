'use client';

import { useEffect, useState } from "react";

export const useCart = ()=>{
  const [cart, setCart] = useState([]);
  const [total, setTotal] = useState(0);

  useEffect(()=>{
    setTotal(()=>{
      let newTotal = 0;
      console.log(cart);
      for(const cartItem of cart){
        console.log(cartItem);
        newTotal += cartItem.price_unit * cartItem.quantity;
      }
      
      console.log(newTotal);
      return newTotal;
    })
  }, [cart])

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
    let deleteItem = false;
    setCart((prev)=>
      prev.map((item) => {
        if(item.cube_id === id){
          if(item.quantity - 1 === 0){
            deleteItem = true;
          }
          return { ...item, quantity: item.quantity - 1 }
        }else{
          return item
        }
      }
    ))
    if(deleteItem){
      setCart((prev)=>
        prev.filter(item => item.cube_id != id)
      );
    }
  }

  return {cart, total, setCart, addToCart, increaseQuantity, decrementQuanity};
}