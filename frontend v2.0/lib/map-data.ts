export interface DeliveryLocation {
  id: string
  lat: number
  lng: number
  type: "primary" | "secondary" | "current"
}

// Sample delivery locations around Singapore
export const deliveryLocations: DeliveryLocation[] = [
  { id: "current", lat: 1.3521, lng: 103.8198, type: "current" },
  { id: "1", lat: 1.3644, lng: 103.8235, type: "secondary" },
  { id: "2", lat: 1.3421, lng: 103.8456, type: "secondary" },
  { id: "3", lat: 1.3321, lng: 103.8621, type: "secondary" },
  { id: "4", lat: 1.3121, lng: 103.8421, type: "primary" },
  { id: "5", lat: 1.3221, lng: 103.8321, type: "primary" },
  { id: "6", lat: 1.3521, lng: 103.8721, type: "secondary" },
  { id: "7", lat: 1.3721, lng: 103.8521, type: "primary" },
  { id: "8", lat: 1.3421, lng: 103.8121, type: "secondary" },
  { id: "9", lat: 1.3621, lng: 103.8921, type: "primary" },
  { id: "10", lat: 1.3321, lng: 103.8221, type: "secondary" },
]
