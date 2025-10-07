'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Rocket } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { NumberInput } from '@/components/number-input';
import Link from 'next/link';
import { MobileNav } from '@/components/mobile-nav';
import { inventoryService } from '@/lib/api/inv-service';
import { hasError } from '@/lib/api-client';
import { toast } from 'sonner';

export default function InventoryFormPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    type: '',
    name: '',
    quantity: 0,
    required: 0,
  });

  // Decode the SKU in case it has special characters like '/'
  const decodedSku = decodeURIComponent(params.id);

  // Fetch the inventory item by SKU
  async function fetchItem() {
    try {
      setLoading(true);

      const response = await inventoryService.getProductBySku(decodedSku);

      if (hasError(response)) {
        toast.error(response.error.error || 'Failed to fetch product');
        router.push('/inventory');
        return;
      }

      const data = response.data;
      if (data) {
        setItem(data);
        setFormData({
          type: data.delivery_type || '',
          name: data.item_name || '',
          quantity: 0, // Inventory doesn't have quantity in current schema
          required: 0,
        });
      }
    } catch (e: any) {
      console.error('Error fetching inventory item:', e.message);
      toast.error('Failed to load product');
      router.push('/inventory');
    } finally {
      setLoading(false);
    }
  }

  // Fetch the item on component mount
  useEffect(() => {
    fetchItem();
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading product...</p>
      </div>
    );
  }

  if (!item) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Product not found</p>
      </div>
    );
  }

  const handleSave = async () => {
    try {
      const response = await inventoryService.updateProduct(decodedSku, {
        delivery_type: formData.type,
        item_name: formData.name,
        // Note: quantity is not part of inventory schema in backend
      });

      if (hasError(response)) {
        toast.error(response.error.error || 'Failed to update product');
        return;
      }

      toast.success('Product updated successfully');
      router.push('/inventory');
    } catch (e: any) {
      console.error('Error saving product:', e.message);
      toast.error('Failed to save product');
    }
  };

  const handleCancel = () => {
    router.push('/inventory');
  };

  return (
    <div className="min-h-screen bg-background flex flex-col pb-20">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-background">
        <div className="flex items-center gap-3 px-4 py-4">
          <Link href="/inventory">
            <Button variant="ghost" size="icon" className="h-10 w-10">
              <ArrowLeft className="h-6 w-6" />
            </Button>
          </Link>
          <Rocket className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-semibold">Inventory Form</h1>
        </div>
      </header>

      {/* Form Content */}
      <main className="flex-1 px-4 py-6 space-y-6">
        <div className="space-y-2">
          <Label htmlFor="type" className="text-base">
            Type
          </Label>
          <Input
            id="type"
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            className="h-14 text-lg"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="name" className="text-base">
            Item<span className="text-amber-500">*</span>
          </Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="h-14 text-lg"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="quantity" className="text-base">
            Quantity<span className="text-amber-500">*</span>
          </Label>
          <NumberInput
            value={formData.quantity}
            onChange={(value) => setFormData({ ...formData, quantity: value })}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="required" className="text-base">
            Required<span className="text-amber-500">*</span>
          </Label>
          <NumberInput
            value={formData.required}
            onChange={(value) => setFormData({ ...formData, required: value })}
          />
        </div>
      </main>

      {/* Bottom Actions */}
      <div className="sticky bottom-16 border-t border-border bg-background px-4 py-4 flex gap-4">
        <Button variant="ghost" onClick={handleCancel} className="flex-1 h-12 text-base">
          Cancel
        </Button>
        <Button onClick={handleSave} className="flex-1 h-12 text-base bg-amber-500 hover:bg-amber-600 text-white">
          Save
        </Button>
      </div>

      <MobileNav />
    </div>
  );
}