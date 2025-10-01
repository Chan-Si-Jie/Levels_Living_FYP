"use client"

import Link from "next/link"
import { ChevronRight, Star } from "lucide-react"
import type { DeliveryDate } from "@/lib/delivery-data"
import { cn } from "@/lib/utils"

interface DeliveryDateListProps {
  dates: DeliveryDate[]
  basePath: string
}

export function DeliveryDateList({ dates, basePath }: DeliveryDateListProps) {
  return (
    <div className="divide-y divide-border">
      {/* All option */}
      <Link
        href={`${basePath}/all`}
        className="flex items-center justify-between px-4 py-4 hover:bg-muted/30 transition-colors"
      >
        <span className="text-base font-medium">All</span>
        <ChevronRight className="h-5 w-5 text-muted-foreground" />
      </Link>

      {/* Individual dates */}
      {dates.map((item) => (
        <Link
          key={item.id}
          href={`${basePath}/${item.id}`}
          className="flex items-center justify-between px-4 py-4 hover:bg-muted/30 transition-colors"
        >
          <div className="flex items-center gap-3">
            {item.isFavorite && <Star className="h-5 w-5 fill-primary text-primary" />}
            <span className={cn("text-base", item.isFavorite && "text-primary font-medium")}>{item.date}</span>
            <span className="flex h-6 min-w-[2rem] items-center justify-center rounded-full bg-muted px-2 text-sm font-medium text-muted-foreground">
              {item.count}
            </span>
          </div>
          <ChevronRight className="h-5 w-5 text-muted-foreground" />
        </Link>
      ))}
    </div>
  )
}
