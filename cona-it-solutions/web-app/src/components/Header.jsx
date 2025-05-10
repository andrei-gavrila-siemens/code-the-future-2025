import Link from "next/link"
import { Cuboid } from "lucide-react"
import { Button } from "@/components/ui/button"
import CartSheet from "./CartSheet"
import { fetchCubes } from "@/lib/models"

export default async function Header() {

  const cubes = await fetchCubes();

  return (
    <nav className="w-full border-b sticky top-0 bg-white">
      <div className="flex items-center justify-between px-8 py-5">
        <Link href="/" className="flex items-center">
          <Cuboid />
          <span className="text-xl font-bold ms-2">CUBURI</span>
        </Link>

        <div className="flex items-center gap-2">
          <Button asChild variant="ghost">
            <Link href="/products" aria-label="View products">
              Products
            </Link>
          </Button>

          <CartSheet cubes={cubes}/>
        </div>
      </div>
    </nav>
  )
}

