import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import cubes from "@/db/cuburi.json";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function isCubeInStock(id, quantity){
  const cube = cubes.find((cube)=> cube.id == id);
  return cube ? cube.stock > quantity : false;
}
