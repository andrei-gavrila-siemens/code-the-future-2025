import React from 'react'
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

export default function CubCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Yellow CUB</CardTitle>
        <CardDescription>Safe, durable, and made with sustainable practices</CardDescription>
      </CardHeader>
      <CardContent>
        <Image src="/yellow.jpg" width={1080} height={1080} alt='cube image' className='w-full'/>
      </CardContent>
      <CardFooter className="flex gap-4">
        <Button>Add to cart</Button>
        <Button variant="secondary">View Product</Button>
      </CardFooter>
    </Card>
  )
}
