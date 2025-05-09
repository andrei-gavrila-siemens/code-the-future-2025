import React from 'react'
import CubCard from "@/components/CubCard";


export default function page() {
  return (
    <div className="flex flex-col">
      <h1 className='text-2xl text-center'>Have a look at our variety of products</h1>
      <div className="flex flex-col md:grid md:grid-cols-2 xl:grid-cols-3 gap-5 mt-4">
        <CubCard />
        <CubCard />
        <CubCard />
        <CubCard />
        <CubCard />
        <CubCard />
        <CubCard />
        <CubCard />
      </div>
    </div>
  )
}
