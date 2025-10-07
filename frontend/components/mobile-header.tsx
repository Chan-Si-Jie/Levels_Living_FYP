"use client"

import type React from "react"
import { useState, useEffect } from "react"

import { ArrowLeft, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRouter, usePathname } from "next/navigation"
import { authService } from "@/lib/api/auth-service"
import { authStorage } from "@/lib/auth-storage"
import { toast } from "sonner"

interface MobileHeaderProps {
  title: string
  icon?: React.ReactNode
  showBack?: boolean
  children?: React.ReactNode
}

export function MobileHeader({ title, icon, showBack = false, children }: MobileHeaderProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [userEmail, setUserEmail] = useState<string>("")

  // Don't show logout on login page
  const showLogout = pathname !== "/login"

  useEffect(() => {
    const user = authStorage.getUserData()
    if (user?.email) {
      setUserEmail(user.email)
    }
  }, [])

  const handleLogout = async () => {
    await authService.logout()
    toast.success("Logged out successfully")
    router.push("/login")
  }

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
        <div className="flex items-center gap-2">
          {children}
          {showLogout && userEmail && (
            <span className="text-sm text-black">
              {userEmail}
            </span>
          )}
          {showLogout && (
            <button
              onClick={handleLogout}
              className="px-3 py-1.5 bg-destructive text-destructive-foreground text-sm font-medium rounded-lg hover:bg-destructive/90 transition-colors"
            >
              Logout
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
