'use client'

import React, { useContext } from 'react'

import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { CartContext } from '@/lib/context/cart'

export default function ProductPage({cube}) {

  const cart = useContext(CartContext);

  return (
    <div className='py-2'>
      <p onClick={()=>{history.back()}} className='hover:underline hover:cursor-pointer'>← Go Back</p>
      <div className='grid sm:grid-cols-2'>
        <Image src={"/"+cube.image} width={1080} height={1080} alt='cube image' className=''/>

        <div className='flex flex-col py-8 pe-8'>
          <h1 className='text-2xl font-bold mb-5'>{cube.name}</h1>
          <p>{cube.description}</p>
          <p className='mt-8'>Price: <span className='font-bold'>{cube.price.toFixed(2)} lei</span> / unit</p>
          <p>In stock: {cube.stock}</p>
          <Button className="mt-8" onClick={()=>{cart.addToCart(cube.id, cube.price, cube.color, cube.stock)}}>Add to cart</Button>
        </div>
      </div>
    </div>
  )
}
