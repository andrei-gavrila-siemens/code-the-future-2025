'use server';

import React from 'react'
import cubes from "@/db/cuburi.json"
import ProductPage from '@/components/pages/ProductPage';

export default async function page({params}) {
  const {id} = await params

  const cube = await cubes.filter((cube) => cube.id == id)[0];

  return (
    <ProductPage cube={cube} />
  )
}
