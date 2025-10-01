"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Minus, Plus } from "lucide-react"

interface NumberInputProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
}

export function NumberInput({ value, onChange, min = 0, max }: NumberInputProps) {
  const handleDecrement = () => {
    const newValue = value - 1
    if (min === undefined || newValue >= min) {
      onChange(newValue)
    }
  }

  const handleIncrement = () => {
    const newValue = value + 1
    if (max === undefined || newValue <= max) {
      onChange(newValue)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number.parseInt(e.target.value) || 0
    if ((min === undefined || newValue >= min) && (max === undefined || newValue <= max)) {
      onChange(newValue)
    }
  }

  return (
    <div className="relative">
      <Input
        type="number"
        value={value}
        onChange={handleInputChange}
        className="pr-24 text-lg h-14"
        min={min}
        max={max}
      />
      <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-2">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={handleDecrement}
          disabled={min !== undefined && value <= min}
          className="h-8 w-8"
        >
          <Minus className="h-5 w-5" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={handleIncrement}
          disabled={max !== undefined && value >= max}
          className="h-8 w-8"
        >
          <Plus className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
}
