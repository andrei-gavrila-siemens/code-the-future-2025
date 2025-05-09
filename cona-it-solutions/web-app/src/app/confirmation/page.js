import { Button } from '@/components/ui/button'
import Link from 'next/link'
import React from 'react'

export default function page() {
  return (
    <div className='flex-1 grid'>
      <div className='place-content-center text-center'>
        <p className='text-2xl'>Thank you for chosing <span className='font-bold'>CUBURI</span></p>
        <p>We hope we can see you again soon!</p>
        <Button className="mt-8" asChild>
          <Link href="/">
            Shop for more
          </Link>
        </Button>
      </div>
    </div>  
  )
}
