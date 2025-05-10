'use server';

import React from 'react'
import ProductPage from '@/components/pages/ProductPage';
import { fetchCubes } from '@/lib/models';

export default async function page({params}) {
  const {id} = await params

  const cubes = await fetchCubes();

  const cube = await cubes.find((cube) => cube.id == id);

  return (
    <ProductPage cube={cube} />
  )
}
