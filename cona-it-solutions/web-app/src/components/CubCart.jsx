import Image from 'next/image'
import React from 'react'
import { Button } from './ui/button'
import Link from 'next/link'

export default function CubCart() {
  return (
    <div className='border-t border-b flex justify-between items-center'>
      <Link className='flex items-center' href="/products/1">
        <Image src="/yellow.jpg" width={100} height={100} alt='cube image' />
        <p>Yellow CUB</p>
      </Link>
      <div className='flex flex-col items-center'>
        <p>10.00 lei</p>
        <div className='flex gap-4 items-center'>
          <Button variant="secondary" size="icon">-</Button>
          <p>1</p>
          <Button size="icon">+</Button>
        </div>
      </div>
    </div>
  )
}
