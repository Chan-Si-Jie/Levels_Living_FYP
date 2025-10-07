"use client"

import type { InventoryItem } from "@/lib/inventory-data"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { ChevronRight } from "lucide-react"

interface InventoryTableProps {
  items: InventoryItem[]
}

export function InventoryTable({ items }: InventoryTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="border-b border-border bg-muted/50">
          <tr>
            <th className="px-4 py-3 text-left text-sm font-semibold">Item</th>
            <th className="px-4 py-3 text-left text-sm font-semibold">Type</th>
            <th className="px-4 py-3 text-right text-sm font-semibold">Quantity</th>
            <th className="px-4 py-3 text-right text-sm font-semibold">Required</th>
            <th className="w-8"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {items.map((item) => {
            // Encode the SKU to handle special characters like '/'
            const encodedId = encodeURIComponent(item.id)
            return (
              <tr key={item.id} className="hover:bg-muted/30 transition-colors">
                <td className="px-4 py-4 text-sm">
                  <Link href={`/inventory/${encodedId}`} className="block">
                    {item.name}
                  </Link>
                </td>
                <td className="px-4 py-4 text-sm text-muted-foreground">
                  <Link href={`/inventory/${encodedId}`} className="block">
                    {item.type}
                  </Link>
                </td>
                <td
                  className={cn(
                    "px-4 py-4 text-right text-sm font-medium",
                    item.quantity === 0 && "text-muted-foreground",
                  )}
                >
                  <Link href={`/inventory/${encodedId}`} className="block">
                    {item.quantity}
                  </Link>
                </td>
                <td
                  className={cn(
                    "px-4 py-4 text-right text-sm font-medium",
                    item.required === 0 && "text-muted-foreground",
                  )}
                >
                  <Link href={`/inventory/${encodedId}`} className="block">
                    {item.required}
                  </Link>
                </td>
                <td className="px-4 py-4">
                  <Link href={`/inventory/${encodedId}`} className="block">
                    <ChevronRight className="h-5 w-5 text-muted-foreground" />
                  </Link>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}