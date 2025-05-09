import React from 'react'
import CubCard from "@/components/CubCard";
import cubes from "@/db/cuburi.json"


export default function page() {
  return (
    <div className="flex flex-col sm:px-8 md:px-20 lg:px-40">
      <h1 className='text-2xl text-center'>Have a look at our variety of products</h1>
      <div className="flex flex-col md:grid md:grid-cols-2 xl:grid-cols-3 gap-5 mt-4">
        {cubes.map((cube, index)=>
          <CubCard cube={cube} key={index}/>
        )}
      </div>
    </div>
  )
}
