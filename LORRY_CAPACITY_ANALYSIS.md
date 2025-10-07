# Lorry Capacity Analysis for Scheduling System

## Vehicle Specifications (from Lalamove)

### 10ft Lorry
- **Capacity:** 200-300 cubic feet
- **Average:** 250 cubic feet (7.08 m³)
- **Use Case:** Small to medium deliveries

### 14ft Lorry
- **Capacity:** 400-500 cubic feet
- **Average:** 450 cubic feet (12.74 m³)
- **Use Case:** Large deliveries, multiple orders

---

## Inventory Volume Analysis (32 Items with Complete Dimensions)

### Volume Distribution

**Extra Large Items (>20 cubic feet):**
1. Vela Wardrobe: **31.08 ft³** (0.88 m³) - $459
2. Osaka XL Shoe Cabinet: **26.70 ft³** (0.76 m³) - $699
3. Texas Tall Shoe Cabinet: **22.10 ft³** (0.63 m³) - $299
4. Vegas Oak Tall Cabinet: **21.97 ft³** (0.62 m³) - $299
5. Monaco Sideboards (x2): **21.47 ft³** (0.61 m³) - $359 each

**Large Items (15-20 cubic feet):**
6. Hamburg 1.6m Sideboards: **17.86 ft³** (0.51 m³) - $369
7. Oxford Bookcase: **17.86 ft³** (0.51 m³) - $299
8. Vegas Tall Cabinets: **16.48 ft³** (0.47 m³) - $249 each

**Medium Items (10-15 cubic feet):**
9-22. Various sideboards, shoe cabinets, TV consoles
- Range: 10-15 ft³ per item

**Small Items (<10 cubic feet):**
23-32. Compact shoe cabinets, benches, bedside tables
- Range: 3-9 ft³ per item

---

## Lorry Capacity Planning

### 10ft Lorry (250 ft³ capacity)

**Scenario 1: Single Large Item Order**
- 1x Vela Wardrobe (31 ft³) + 8x Small Cabinets (~48 ft³) = **~79 ft³**
- **Utilization:** 32% ✅ Room for more

**Scenario 2: Mixed Furniture Order**
- 2x Monaco Sideboards (43 ft³) + 4x Medium Cabinets (48 ft³) = **~91 ft³**
- **Utilization:** 36% ✅

**Scenario 3: Multiple Small Orders**
- 10x Vegas 90cm Cabinets (87.5 ft³) = **~88 ft³**
- **Utilization:** 35% ✅

**Maximum Items (Small cabinets only):**
- 250 ft³ ÷ 5.83 ft³ = **~43 small Vegas cabinets**
- 250 ft³ ÷ 3.18 ft³ = **~79 Cubo bedside tables**

### 14ft Lorry (450 ft³ capacity)

**Scenario 1: High-Value Large Items**
- 1x Vela Wardrobe (31 ft³) + 1x Osaka Cabinet (27 ft³) + 8x Medium items (100 ft³) = **~158 ft³**
- **Utilization:** 35% ✅

**Scenario 2: Full Load**
- 10x Hamburg Sideboards (134 ft³) + 8x Texas Cabinets (94 ft³) = **~228 ft³**
- **Utilization:** 51% ✅ Efficient

**Scenario 3: Maximum Small Items**
- 450 ft³ ÷ 5.83 ft³ = **~77 small Vegas cabinets**

---

## Key Insights

### 1. Volume Efficiency (Packing Factor)
- **Actual usable space:** 60-70% of total capacity (due to irregular shapes)
- **10ft lorry effective:** 150-175 ft³ (4.2-5.0 m³)
- **14ft lorry effective:** 270-315 ft³ (7.6-8.9 m³)

### 2. Critical Items (Large footprint)
These items should trigger **14ft lorry** selection:
- Vela Wardrobe (31 ft³)
- Osaka XL Cabinet (27 ft³)
- Any order with 3+ large sideboards (>20 ft³ each)

### 3. Weight Considerations
Most items are furniture (not weight-constrained), but:
- Mattresses: 1000kg weight (currently in database but no dimensions)
- Volume is PRIMARY constraint, not weight

### 4. Assembly Impact
- **30 out of 32 items** require assembly
- Assembly time: **30-60 minutes per item**
- This affects **time slots**, not vehicle capacity

---

## Scheduling Algorithm Recommendations

### Option A: Simple Volume-Based (Current System)
```javascript
function selectLorry(orderItems) {
  const totalVolume = orderItems.reduce((sum, item) => sum + item.volume_cubic_feet, 0);
  const PACKING_EFFICIENCY = 0.65; // 65% usable space
  const adjustedVolume = totalVolume / PACKING_EFFICIENCY;

  if (adjustedVolume <= 250) {
    return "10ft"; // Fits in 10ft lorry
  } else if (adjustedVolume <= 450) {
    return "14ft"; // Needs 14ft lorry
  } else {
    return "MULTIPLE_TRIPS"; // Split into 2+ deliveries
  }
}
```

### Option B: Smart Capacity Planning (Recommended)
```javascript
function smartLorrySelection(orders, date) {
  // Group orders by delivery area (postal code prefix)
  const ordersByArea = groupByPostalCode(orders);

  // Calculate volume per area
  const areaVolumes = ordersByArea.map(area => ({
    area: area.postal_prefix,
    volume: calculateTotalVolume(area.orders),
    orderCount: area.orders.length,
    hasLargeItems: area.orders.some(o => o.items.some(i => i.volume_cubic_feet > 20))
  }));

  // Determine lorry type per route
  return areaVolumes.map(area => {
    const adjustedVolume = area.volume / 0.65; // Packing efficiency

    if (area.hasLargeItems || adjustedVolume > 250) {
      return { area: area.area, lorry: "14ft", capacity: 450, volume: area.volume };
    } else {
      return { area: area.area, lorry: "10ft", capacity: 250, volume: area.volume };
    }
  });
}
```

### Option C: Cost Optimization
```javascript
function optimizeDeliveryCost(orders) {
  // Assume: 10ft = $80, 14ft = $120 per trip
  const COST_10FT = 80;
  const COST_14FT = 120;

  const totalVolume = calculateTotalVolume(orders);
  const adjustedVolume = totalVolume / 0.65;

  // Option 1: Single 14ft lorry
  const cost_single_14ft = adjustedVolume <= 450 ? COST_14FT : COST_14FT * 2;

  // Option 2: Multiple 10ft lorries
  const num_10ft_lorries = Math.ceil(adjustedVolume / 250);
  const cost_multiple_10ft = num_10ft_lorries * COST_10FT;

  // Return cheapest option
  return cost_single_14ft < cost_multiple_10ft
    ? { lorry: "14ft", trips: 1, cost: cost_single_14ft }
    : { lorry: "10ft", trips: num_10ft_lorries, cost: cost_multiple_10ft };
}
```

---

## Frontend Display Recommendations

### 1. Show Volume on Schedule Page
For each unscheduled order, display:
```
Order #ORD-123
├─ Monaco Sideboard (21.5 ft³) 🔧
├─ Vegas Cabinet (8.8 ft³) 🔧
└─ Total: 30.3 ft³
```

### 2. Capacity Indicator
When selecting orders:
```
Selected Orders (5 orders, 12 items)
┌─────────────────────────────────────┐
│ Total Volume: 145.2 ft³             │
│ Recommended: 10ft Lorry (58% full)  │
│ Assembly Time: ~6 hours             │
└─────────────────────────────────────┘
```

### 3. Smart Warnings
```
⚠️ Warning: Vela Wardrobe (200cm tall) - May not fit in elevator
⚠️ Note: 8 items require assembly (~6 hours total)
✅ Recommended: 14ft Lorry for optimal space
```

### 4. Multi-Trip Planning
If total volume exceeds capacity:
```
❌ Cannot fit in single lorry
💡 Suggestion:
   Trip 1: 14ft Lorry (350 ft³) - Orders #1-8
   Trip 2: 10ft Lorry (120 ft³) - Orders #9-12
```

---

## Database Schema Updates Needed

### Add volume_cubic_feet to order_items table
```sql
ALTER TABLE order_items
ADD COLUMN volume_cubic_feet DECIMAL(10,2) COMMENT 'Item volume in cubic feet';

-- Populate from inventory dimensions
UPDATE order_items oi
JOIN inventory i ON oi.sku = i.sku
SET oi.volume_cubic_feet = (
  JSON_EXTRACT(i.dimensions, '$.width') *
  JSON_EXTRACT(i.dimensions, '$.height') *
  JSON_EXTRACT(i.dimensions, '$.length')
) / 1000000 * 35.3147
WHERE i.dimensions IS NOT NULL
  AND i.dimensions NOT LIKE '%null%';
```

### Add lorry_type to delivery_schedules table
```sql
ALTER TABLE delivery_schedules
ADD COLUMN lorry_type ENUM('10ft', '14ft') DEFAULT '10ft',
ADD COLUMN total_volume_cubic_feet DECIMAL(10,2) COMMENT 'Total volume for route',
ADD COLUMN capacity_utilization DECIMAL(5,2) COMMENT 'Percentage of lorry used';
```

---

## Cost Analysis Example

### Scenario: 15 Orders on Oct 7, 2025

**Current Method (No volume planning):**
- Assume 14ft lorry for all deliveries
- Cost: $120 per trip
- Total: **$120**

**Optimized Method (Volume-based):**
- Orders 1-10: Total 180 ft³ → **10ft lorry ($80)**
- Orders 11-15: Total 95 ft³ → **10ft lorry ($80)**
- Total: **$160** but 2 routes (more flexible scheduling)

**OR**
- All 15 orders: Total 275 ft³ → **Single 14ft lorry ($120)** ✅ Best option
- Capacity: 275 / 450 = **61% utilization**

---

## Implementation Priority

### Phase 1: Basic Volume Tracking ✅
1. Add volume calculations to order creation
2. Display total volume on schedule page
3. Show lorry recommendation

### Phase 2: Smart Capacity Planning
1. Implement lorry selection algorithm
2. Add capacity warnings
3. Multi-trip detection

### Phase 3: Cost Optimization
1. Track lorry rental costs
2. Optimize route-to-lorry assignment
3. Report cost savings

---

---

## Complete Item Volume List (All 32 Items)

| Rank | SKU | Item Name | Width (cm) | Height (cm) | Length (cm) | Volume (m³) | Volume (ft³) | Price | Assembly |
|------|-----|-----------|------------|-------------|-------------|-------------|--------------|-------|----------|
| 1 | WD8003/3036-AD | Vela 80cm Modular Wardrobe | 80 | 200 | 55 | 0.880 | 31.08 | $459 | Yes |
| 2 | SB1204/3045-AD | Osaka 1.2m Maple XL Shoe Cabinet | 120 | 180 | 35 | 0.756 | 26.70 | $699 | Yes |
| 3 | SC18(X2)/WAL | Texas Walnut 1.2m Wide 1.63m High | 120 | 163 | 32 | 0.626 | 22.10 | $299 | Yes |
| 4 | SC5(X2) | Vegas Oak 1.2m Wide 1.62m High | 120 | 162 | 32 | 0.622 | 21.97 | $299 | Yes |
| 5 | SI1685/3075-AD | Monaco 1.6m Walnut 4-Door Sideboard | 160 | 95 | 40 | 0.608 | 21.47 | $359 | Yes |
| 6 | SI1685/3045-AD | Monaco 1.6m Maple 4-Door Sideboard | 160 | 95 | 40 | 0.608 | 21.47 | $359 | Yes |
| 7 | SR7/3045WH(Premium)-AD | Hamburg 1.6m Maple/White Sideboard | 160 | 79 | 40 | 0.506 | 17.86 | $369 | Yes |
| 8 | SS6020/3075 | Oxford 60cm Walnut Bookcase | 160 | 79 | 40 | 0.506 | 17.86 | $299 | Yes |
| 9 | SC15(X2) | Vegas Oak 90cm Wide 1.62m High | 90 | 162 | 32 | 0.467 | 16.48 | $249 | No |
| 10 | SC15(X2)/WAL | Vegas Walnut 90cm Wide 1.62m High | 90 | 162 | 32 | 0.467 | 16.48 | $249 | Yes |
| 11 | SR6/3036WH-AD | Hamburg 1.4m Pine/White Sideboard | 140 | 79 | 40 | 0.442 | 15.62 | $329 | Yes |
| 12 | SR7/3036(Premium)-AD | Hamburg 1.6m Pine Sideboard | 140 | 79 | 40 | 0.442 | 15.62 | $369 | Yes |
| 13 | SB1283/3075-AD | Richmond 1.2m Walnut Shoe Cabinet | 120 | 100 | 36 | 0.432 | 15.26 | $299 | Yes |
| 14 | SI1295/3036-AD | Manhattan 1.2m Pine Flat Top | 120 | 90 | 40 | 0.432 | 15.26 | $329 | Yes |
| 15 | T1013 | Pixel 5-Drawer Desk | 100 | 75 | 55 | 0.412 | 14.57 | $399 | Yes |
| 16 | SR5/3036WH | Hamburg 1.2m Pine/White Sideboard | 120 | 79 | 40 | 0.379 | 13.39 | $299 | Yes |
| 17 | SR5/3075(Premium) | Hamburg 1.2m Walnut Sideboard | 120 | 79 | 40 | 0.379 | 13.39 | $299 | Yes |
| 18 | TV24/1.6/3075-AD | Hamburg 1.6m Walnut TV Console | 160 | 54 | 40 | 0.346 | 12.20 | $269 | Yes |
| 19 | SC18/WAL | Texas 1.2m Walnut Shoe Cabinet | 120 | 86.5 | 32 | 0.332 | 11.73 | $169 | Yes |
| 20 | SC18/OAK | Texas 1.2m Oak Shoe Cabinet | 120 | 86.5 | 32 | 0.332 | 11.73 | $169 | Yes |
| 21 | SC5/WAL | Vegas 1.2m Walnut 4-Door | 120 | 86 | 32 | 0.330 | 11.66 | $169 | Yes |
| 22 | TV1634/3018-AD | Paisley 1.6m Oak TV Console | 160 | 50 | 40 | 0.320 | 11.30 | $269 | Yes |
| 23 | SC15/WAL | Vegas 90cm Walnut Shoe Cabinet | 90 | 86 | 32 | 0.248 | 8.75 | $149 | Yes |
| 24 | SC15 | Vegas 90cm Oak Shoe Cabinet | 90 | 86 | 32 | 0.248 | 8.75 | $149 | Yes |
| 25 | SB8083/4049 | Richie 80cm Shoe Cabinet | 80 | 87 | 35 | 0.244 | 8.60 | $299 | Yes |
| 26 | SB1048/3075 | Vernetta 100cm Walnut Shoe Bench | 100 | 48 | 40 | 0.192 | 6.78 | $299 | No |
| 27 | SR4/3075-AD | Munich 1.2m Walnut Highboard | 120 | 37 | 40 | 0.178 | 6.27 | $399 | Yes |
| 28 | SC5 | Vegas 1.2m Oak Shoe Cabinet | 60 | 86 | 32 | 0.165 | 5.83 | $169 | Yes |
| 29 | SC4/WAL | Vegas 60cm Walnut 2-Door | 60 | 86 | 32 | 0.165 | 5.83 | $119 | Yes |
| 30 | SC4 | Vegas 60cm Oak Shoe Cabinet | 60 | 86 | 32 | 0.165 | 5.83 | $119 | Yes |
| 31 | SB4311/3045WH-AD | Eden 35cm Maple/White Slim | 35 | 100 | 35 | 0.122 | 4.33 | $259 | Yes |
| 32 | BT4550/3101 | Cubo 45cm Ash/White Bedside | 45 | 50 | 40 | 0.090 | 3.18 | $199 | Yes |

---

## Lorry Selection Quick Reference

### Packing Efficiency Factor: 65%

**Effective Capacities:**
- **10ft Lorry:** 163 ft³ usable (250 ft³ × 0.65)
- **14ft Lorry:** 293 ft³ usable (450 ft³ × 0.65)

### Decision Matrix

| Total Volume | Lorry Type | Capacity Usage | Action |
|--------------|------------|----------------|--------|
| 0 - 163 ft³ | 10ft | Optimal | ✅ Book 10ft lorry |
| 164 - 250 ft³ | 10ft or 14ft | Consider cost | ⚠️ Compare pricing |
| 251 - 293 ft³ | 14ft | Optimal | ✅ Book 14ft lorry |
| 294 - 450 ft³ | 14ft | Tight fit | ⚠️ Repack or split |
| 451+ ft³ | Multiple | Over capacity | ❌ Must split into 2+ trips |

### Trigger Items (Always use 14ft lorry if order contains):

1. **Vela Wardrobe** (31 ft³) - Too large for optimal 10ft packing
2. **Osaka XL Cabinet** (27 ft³) - Takes up significant space
3. **3+ Monaco/Large Sideboards** (21 ft³ each) - Combined volume too high
4. **Any combination totaling >163 ft³**

---

## Integration with Current 18-Location Limit

Your current system limits schedules to **18 locations per day** (3rd party delivery agreement). With volume planning, you now have **two constraints**:

### Dual Constraint Logic:

```javascript
function validateSchedule(selectedOrders) {
  const locationCount = selectedOrders.length;
  const totalVolume = calculateTotalVolume(selectedOrders);
  const effectiveVolume = totalVolume / 0.65; // Apply packing factor

  // Check both constraints
  const locationOK = locationCount <= 18;
  const volumeOK = effectiveVolume <= 450; // 14ft lorry max

  if (!locationOK && !volumeOK) {
    return {
      valid: false,
      error: "Exceeds both location (18) and volume (450 ft³) limits",
      suggestion: "Remove large items or reduce order count"
    };
  }

  if (!locationOK) {
    return {
      valid: false,
      error: `Too many locations: ${locationCount}/18`,
      suggestion: "Reduce number of orders"
    };
  }

  if (!volumeOK) {
    return {
      valid: false,
      error: `Volume too high: ${effectiveVolume.toFixed(1)}/450 ft³`,
      suggestion: "Split large items into separate route",
      recommendedSplit: suggestRouteSplit(selectedOrders)
    };
  }

  // Both constraints satisfied
  return {
    valid: true,
    locationCount,
    totalVolume: effectiveVolume.toFixed(1),
    recommendedLorry: effectiveVolume <= 163 ? "10ft" : "14ft",
    utilizationPercent: (effectiveVolume / (effectiveVolume <= 163 ? 163 : 293) * 100).toFixed(1)
  };
}
```

### Real-World Scenarios:

**Scenario 1: Volume-Constrained (Hit volume limit before location limit)**
```
15 orders selected
Total volume: 320 ft³ (adjusted)
Status: ❌ Exceeds 14ft capacity (293 ft³)
Action: Split into 2 routes OR remove 3 large items
```

**Scenario 2: Location-Constrained (Hit location limit before volume limit)**
```
18 orders selected (all small cabinets)
Total volume: 105 ft³ (adjusted)
Status: ✅ Fits in 10ft lorry (163 ft³)
Lorry: 10ft (64% utilization)
```

**Scenario 3: Balanced Load**
```
12 orders selected
Total volume: 180 ft³ (adjusted)
Status: ✅ Within limits
Lorry: 14ft (61% utilization) - Optimal
```

---

## Frontend Display Examples

### Schedule Page - Selection Summary

```typescript
interface ScheduleSummary {
  ordersSelected: number;
  maxOrders: 18;
  totalItems: number;
  totalVolume: number; // cubic feet
  effectiveVolume: number; // with packing factor
  recommendedLorry: "10ft" | "14ft";
  capacity: number; // 163 or 293
  utilizationPercent: number;
  warnings: string[];
}

// Example display:
┌──────────────────────────────────────────────┐
│ Schedule Summary                             │
├──────────────────────────────────────────────┤
│ 📦 Orders Selected: 12 / 18                  │
│ 📋 Total Items: 28                           │
│                                              │
│ 📊 Volume Analysis:                          │
│   Raw Volume: 142.5 ft³                      │
│   Adjusted (65%): 219.2 ft³                  │
│                                              │
│ 🚚 Recommended Lorry: 14ft                   │
│   Capacity: 219.2 / 293 ft³ (75% full)       │
│                                              │
│ ⚠️ Warnings:                                 │
│   • Contains Vela Wardrobe (200cm tall)      │
│   • 18 items require assembly (~9 hrs)       │
│                                              │
│ ✅ Status: Ready to schedule                 │
└──────────────────────────────────────────────┘
```

### Individual Order Display with Volume

```typescript
Order #ORD-20250107-001
Customer: John Tan | Postal: 520123
┌─────────────────────────────────────────┐
│ Items:                                  │
│ 1x Monaco Sideboard (21.5 ft³) 🔧⚠️    │
│ 2x Vegas Cabinet (17.5 ft³ total) 🔧   │
│ 1x Cubo Bedside (3.2 ft³) 🔧           │
├─────────────────────────────────────────┤
│ Total: 42.2 ft³ | Assembly: ~2.5 hrs   │
│ 🏋️ Requires 2-person lift              │
└─────────────────────────────────────────┘

Legend:
🔧 = Assembly required
⚠️ = Large item (>20 ft³)
🏋️ = Heavy/Special handling
📏 = Tall item (>180cm)
```

### Volume-Based Warning System

```typescript
// Warning levels based on capacity
if (utilizationPercent < 50) {
  status = "🟢 Low utilization - can add more orders";
} else if (utilizationPercent < 75) {
  status = "🟡 Good utilization - optimal range";
} else if (utilizationPercent < 90) {
  status = "🟠 High utilization - near capacity";
} else if (utilizationPercent < 100) {
  status = "🔴 Very high - repack carefully";
} else {
  status = "❌ Over capacity - must split";
}
```

---

## Cost-Benefit Analysis

### Current System (No Volume Planning)
- **Pro:** Simple, always use 14ft lorry
- **Con:** Wasteful for small orders (low utilization)
- **Cost:** Fixed $120 per route

### Volume-Optimized System
- **Pro:** Match lorry size to actual needs
- **Pro:** Save costs on small orders (use 10ft @ $80)
- **Con:** More complex planning
- **Savings:** Up to 33% on small order days

### Monthly Savings Estimate (20 delivery days):
```
Scenario: 40% of days have small orders (<163 ft³)

Current: 20 days × $120 = $2,400/month
Optimized: 12 days × $120 + 8 days × $80 = $2,080/month

Monthly Savings: $320 (13%)
Annual Savings: $3,840
```

---

## Technical Implementation Checklist

### Backend (OrderMS + InventoryMS)

- [ ] **Database Updates**
  - [ ] Add `volume_cubic_feet` to `order_items` table
  - [ ] Add `volume_m3` to `inventory` table
  - [ ] Add `lorry_type`, `total_volume_cubic_feet`, `capacity_utilization` to `delivery_schedules`
  - [ ] Backfill existing inventory with volume calculations

- [ ] **OrderMS API Endpoints**
  - [ ] `GET /orders/unscheduled` - Add volume calculations to response
  - [ ] `POST /orders/schedule` - Add lorry type selection logic
  - [ ] `GET /orders/calculate-volume` - New endpoint for real-time volume calculation
  - [ ] Update schedule creation to validate volume constraints

- [ ] **InventoryMS Integration**
  - [ ] Add volume calculation method in InventoryMS
  - [ ] Expose volume data via `/inventory/delivery-requirements` endpoint

### Frontend (Schedule Page)

- [ ] **UI Components**
  - [ ] Volume summary card showing total volume, lorry recommendation
  - [ ] Individual order volume display
  - [ ] Capacity utilization progress bar
  - [ ] Warning system for over-capacity scenarios

- [ ] **Logic Implementation**
  - [ ] Calculate total volume when selecting orders
  - [ ] Show lorry recommendation dynamically
  - [ ] Implement packing efficiency factor (65%)
  - [ ] Add volume-based validation before schedule creation
  - [ ] Display split suggestions if over capacity

- [ ] **Visual Enhancements**
  - [ ] Icons for large items (⚠️), assembly (🔧), tall items (📏)
  - [ ] Color-coded capacity indicators (green/yellow/red)
  - [ ] Lorry type selector (manual override option)

### Testing Scenarios

- [ ] Test with all small items (should recommend 10ft)
- [ ] Test with Vela Wardrobe (should recommend 14ft)
- [ ] Test with 20+ small items (should hit location limit first)
- [ ] Test with 10 large items (should hit volume limit first)
- [ ] Test over-capacity scenario (should show split suggestions)
- [ ] Test edge case: exactly 163 ft³ (boundary between 10ft/14ft)

---

**Next Steps for Implementation:**
1. Review this analysis document with stakeholders
2. Decide on implementation priority (Phase 1, 2, or 3)
3. Update database schema with volume fields
4. Integrate volume calculation into OrderMS
5. Update frontend schedule page with capacity indicators
6. Implement lorry selection logic
7. Test with real order data
8. Train HQ staff on new volume-based scheduling

---

**Document Version:** 1.0
**Last Updated:** 2025-10-07
**Data Source:** 32 inventory items with complete dimensions
**Reference Files:**
- `inventory_volumes_analysis.csv` - Complete volume calculations
- `inventory_complete_dimensions.csv` - Raw dimension data
