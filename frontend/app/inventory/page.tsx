'use client';

import { useEffect, useState } from 'react';
import { MobileHeader } from "@/components/mobile-header";
import { MobileNav } from "@/components/mobile-nav";
import { InventoryTable } from "@/components/inventory-table";
import { Button } from "@/components/ui/button";
import { Warehouse, Plus } from "lucide-react";
import { inventoryService } from "@/lib/api/inv-service";
import { hasError } from "@/lib/api-client";
import { toast } from "sonner";

export default function InventoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch inventory items from the backend
  async function fetchProducts() {
    try {
      setLoading(true);

      const response = await inventoryService.getProducts({
        limit: 50,
        offset: 0
      });

      if (hasError(response)) {
        toast.error(response.error.error || "Failed to fetch inventory");
        return;
      }

      const products = response.data?.products || [];
      const rows = products.map((p: any) => ({
        id: p.sku,
        name: [p.item_name, p.variant].filter(Boolean).join(' · '),
        sku: p.sku,
        quantity: p.quantity || 0,
        location: p.storage_location || '—',
        status: p.showroom_item ? 'Showroom' : (p.special_handling_required ? 'Special' : 'Normal'),
        price: typeof p.unit_price === 'number' ? `$${p.unit_price.toFixed(2)}` : undefined,
      }));

      setItems(rows);
    } catch (e: any) {
      console.error("Error fetching products:", e.message);
      toast.error("Failed to load inventory");
    } finally {
      setLoading(false);
    }
  }

  // Fetch products on component mount
  useEffect(() => {
    fetchProducts();
  }, []);

  return (
    <div className="min-h-screen pb-20">
      {/* Mobile Header */}
      <MobileHeader title="Inventory" icon={<Warehouse className="h-6 w-6 text-primary" />} />

      {/* Main Content */}
      <main className="p-4">
        {/* Loading State */}
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading inventory...</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No inventory items found</p>
        ) : (
          <InventoryTable items={items} />
        )}
      </main>

      {/* Floating Refresh Button */}
      <Button
        size="icon"
        className="fixed bottom-24 right-6 h-14 w-14 rounded-full shadow-lg"
        onClick={fetchProducts}
        title="Refresh inventory"
      >
        <Plus className="h-6 w-6" />
      </Button>

      {/* Mobile Navigation */}
      <MobileNav />
    </div>
  );
}
