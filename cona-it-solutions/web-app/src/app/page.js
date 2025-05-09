import CubCard from "@/components/CubCard";
import Image from "next/image";
import Link from "next/link";


// const cuburi = [
//   {
//     'name
//   }
// ]

export default function Home() {
  return (
    <div className="flex flex-col">
      <h1 className="text-2xl">Welcome to <span className="font-bold">CUBURI</span></h1>
      <p className="text-gray-500">Discover smart, colorful, and educational toy cubes — designed to inspire creativity and curiosity in every child.</p>
      
      <p className="text-center mt-8 mb-4 text-xl">Our Most Wanted Products</p>
      <div className="flex flex-col md:grid md:grid-cols-2 xl:grid-cols-3 gap-5">
        <CubCard />
        <CubCard />
        <CubCard />
      </div>
      <Link href="/products" className="self-center mt-4 hover:underline">See more ...</Link>
    </div>
  );
}
