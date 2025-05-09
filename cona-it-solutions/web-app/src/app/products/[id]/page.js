'use client';

import { Button } from '@/components/ui/button'
import Image from 'next/image'
import Link from 'next/link'
import React from 'react'

export default function page() {
  return (
    <div className='py-2'>
      <p onClick={()=>{history.back()}} className='hover:underline hover:cursor-pointer'>← Go Back</p>
      <div className='grid sm:grid-cols-2'>
        <Image src="/yellow.jpg" width={1080} height={1080} alt='cube image' className=''/>

        <div className='flex flex-col py-8 pe-8'>
          <h1 className='text-2xl font-bold mb-5'>Yellow CUB</h1>
          <p>Safe, durable, and made with sustainable practices</p>
          <p className='mt-8'>Price: <span className='font-bold'>10.00 lei</span> / buc</p>
          <p>In stock: 5</p>
          <Button className="mt-8">Add to cart</Button>
        </div>
      </div>
    </div>
  )
}
