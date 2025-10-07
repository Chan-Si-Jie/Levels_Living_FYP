"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Package, Truck, Warehouse, MapPin, Calendar, BarChart3, Building2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"
import { authStorage } from "@/lib/auth-storage"

const driverNavItems = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { href: "/pack", label: "Pack", icon: Package },
  { href: "/delivery", label: "Delivery", icon: Truck },
  { href: "/inventory", label: "Inventory", icon: Warehouse },
  { href: "/overview", label: "Overview", icon: MapPin },
]

const hqNavItems = [
  { href: "/hq-dashboard", label: "Dashboard", icon: Building2 },
  { href: "/schedule", label: "Schedule", icon: Calendar },
  { href: "/pack", label: "Pack", icon: Package },
  { href: "/delivery", label: "Delivery", icon: Truck },
  { href: "/inventory", label: "Inventory", icon: Warehouse },
  { href: "/overview", label: "Overview", icon: MapPin },
]

export function MobileNav() {
  const pathname = usePathname()
  const [userRole, setUserRole] = useState<string>("")

  useEffect(() => {
    const user = authStorage.getUserData()
    if (user?.role) {
      setUserRole(user.role)
    }
  }, [])

  // Choose navigation items based on user role
  // Admin and HQ users get the HQ navigation (with Schedule)
  // Driver users get the driver navigation (without Schedule)
  const navItems = (userRole === 'admin' || userRole === 'hq') ? hqNavItems : driverNavItems

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t border-border bg-background">
      <div className="flex items-center justify-around">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-1 flex-col items-center gap-1 py-3 text-xs transition-colors",
                isActive ? "bg-accent text-accent-foreground" : "text-muted-foreground hover:text-foreground",
              )}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
