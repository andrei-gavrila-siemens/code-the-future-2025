'use client';

import Image from 'next/image'
import React, { useContext, useEffect, useState } from 'react'
import { Button } from './ui/button'
import Link from 'next/link'
import { CartContext } from '@/lib/context/cart'

export default function CubCart({cube}) {

  const {cart, increaseQuantity, decrementQuanity} = useContext(CartContext);
  const [cubeCartItem, setCubeCartItem] = useState({});

  useEffect(()=>{
    setCubeCartItem(()=>
      cart.find(cartItem => cartItem.cube_id == cube.id)
    );
  }, [cart])

  return (
    <div className='border-t border-b flex justify-between items-center'>
      <Link className='flex items-center' href="/products/1">
        <Image src={cube.image} width={100} height={100} alt='cube image' />
        <p>{cube.name}</p>
      </Link>
      <div className='flex flex-col items-center'>
        <p>{(cube.price * cubeCartItem.quantity).toFixed(2)} lei</p>
        <div className='flex gap-4 items-center'>
          <Button variant="secondary" size="icon" onClick={()=>{decrementQuanity(cube.id)}}>-</Button>
          <p>{cubeCartItem.quantity}</p>
          <Button size="icon" onClick={()=>{increaseQuantity(cube.id)}}>+</Button>
        </div>
      </div>
    </div>
  )
}
