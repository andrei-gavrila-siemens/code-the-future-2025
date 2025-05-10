'use client';

import React, { useContext } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from './ui/button'
import Image from 'next/image'
import Link from 'next/link'
import { CartContext } from '@/lib/context/cart'

export default function CubCard({cube}) {

  const cart = useContext(CartContext);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{cube.name}</CardTitle>
        <CardDescription>{cube.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Image src={"/"+cube.image} width={1080} height={1080} alt='cube image' className='w-full'/>
      </CardContent>
      <CardFooter className="flex gap-4">
        <Button onClick={()=>{cart.addToCart(cube.id, cube.price, cube.color, cube.stock)}}>Add to cart</Button>
        <Link href={`/products/${cube.id}`}>
          <Button variant="secondary">View Product</Button>
        </Link>
      </CardFooter>
    </Card>
  )
}
