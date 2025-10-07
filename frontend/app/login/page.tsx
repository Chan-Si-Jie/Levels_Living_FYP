"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { authService } from "@/lib/api/auth-service"
import { hasError } from "@/lib/api-client"
import { toast } from "sonner"
import { Loader2 } from "lucide-react"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    const response = await authService.login({ email, password })

    if (hasError(response)) {
      toast.error(response.error.error || "Login failed")
      setLoading(false)
      return
    }

    toast.success("Login successful!")

    // Redirect based on user role
    const user = response.data?.user
    if (user?.role === "driver") {
      router.push("/dashboard")
    } else if (user?.role === "hq" || user?.role === "admin") {
      router.push("/hq-dashboard")
    } else {
      router.push("/")
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Levels Living
            <br />
            Delivery System
          </CardTitle>
          <CardDescription className="text-center">
            Enter your credentials: (HQ/Driver)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="your.email@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Sign In
            </Button>
          </form>

          <div className="mt-4 text-center text-sm text-muted-foreground">
            <p>Test Accounts:</p>
            <p className="text-xs mt-1">Driver: driver@levels.sg / password123</p>
            <p className="text-xs">HQ: mervin@levels.sg / password123</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
