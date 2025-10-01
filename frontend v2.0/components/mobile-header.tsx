"use client"

import type React from "react"

import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

interface MobileHeaderProps {
  title: string
  icon?: React.ReactNode
  showBack?: boolean
  children?: React.ReactNode
}

export function MobileHeader({ title, icon, showBack = false, children }: MobileHeaderProps) {
  const router = useRouter()

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-3">
          {showBack ? (
            <Button variant="ghost" size="icon" className="h-9 w-9" onClick={() => router.back()}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
          ) : null}
          <div className="flex items-center gap-2">
            {icon}
            <h1 className="text-xl font-semibold">{title}</h1>
          </div>
        </div>
        {children && <div className="flex items-center gap-2">{children}</div>}
      </div>
    </header>
  )
}
