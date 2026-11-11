"""Hyperlocal Quick-Commerce Dark Store Allocation, Geofencing & 10-Minute Dispatch Engine."""

import math
import time
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DarkStore(BaseModel):
    store_id: str
    store_name: str
    latitude: float
    longitude: float
    max_delivery_radius_km: float = 3.5  # 10-15 minute delivery radius
    is_active: bool = True
    inventory: Dict[str, int] = Field(default_factory=dict)  # sku -> available quantity


class QuickOrderItem(BaseModel):
    sku: str
    quantity: int
    unit_price: float


class QuickCommerceOrder(BaseModel):
    order_id: str
    customer_id: str
    customer_lat: float
    customer_lon: float
    items: List[QuickOrderItem]
    total_amount: float
    assigned_store_id: str
    status: str = "RECEIVED"  # RECEIVED, PICKING, PACKED, OUT_FOR_DELIVERY, DELIVERED
    assigned_rider_id: Optional[str] = None
    created_at: float = Field(default_factory=time.time)


class QuickCommerceEngine:
    """Manages dark store geofencing, sub-second inventory reservations, and rider dispatches."""

    def __init__(self):
        self.stores: Dict[str, DarkStore] = {}
        self.orders: Dict[str, QuickCommerceOrder] = {}
        self.riders: Dict[str, Dict[str, Any]] = {}

    def register_dark_store(self, store: DarkStore) -> DarkStore:
        self.stores[store.store_id] = store
        return store

    def add_rider(self, rider_id: str, name: str, current_store_id: str):
        self.riders[rider_id] = {
            "rider_id": rider_id,
            "name": name,
            "store_id": current_store_id,
            "is_busy": False
        }

    @staticmethod
    def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates distance between two GPS coordinates in kilometers."""
        r = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2.0) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 2)

    def find_nearest_serviceable_dark_store(self, customer_lat: float, customer_lon: float) -> Optional[DarkStore]:
        nearest_store = None
        min_dist = float("inf")

        for store in self.stores.values():
            if not store.is_active:
                continue
            dist = self.calculate_haversine_distance(customer_lat, customer_lon, store.latitude, store.longitude)
            if dist <= store.max_delivery_radius_km and dist < min_dist:
                min_dist = dist
                nearest_store = store

        return nearest_store

    def place_quick_order(
        self,
        customer_id: str,
        customer_lat: float,
        customer_lon: float,
        items: List[QuickOrderItem]
    ) -> QuickCommerceOrder:
        store = self.find_nearest_serviceable_dark_store(customer_lat, customer_lon)
        if not store:
            raise ValueError("Location not serviceable within 10-minute dark store delivery radius.")

        # Check inventory availability in the selected dark store
        for item in items:
            available_qty = store.inventory.get(item.sku, 0)
            if available_qty < item.quantity:
                raise ValueError(f"SKU {item.sku} is out of stock or insufficient in dark store {store.store_name}.")

        # Deduct / reserve inventory atomically
        for item in items:
            store.inventory[item.sku] -= item.quantity

        total_val = sum(it.quantity * it.unit_price for it in items)
        order_id = f"QCOM-{uuid.uuid4().hex[:8].upper()}"

        order = QuickCommerceOrder(
            order_id=order_id,
            customer_id=customer_id,
            customer_lat=customer_lat,
            customer_lon=customer_lon,
            items=items,
            total_amount=round(total_val, 2),
            assigned_store_id=store.store_id,
            status="PICKING"
        )
        self.orders[order_id] = order
        return order

    def dispatch_order(self, order_id: str) -> Dict[str, Any]:
        """Assigns an idle rider from the dark store and triggers delivery dispatch."""
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Order not found.")

        # Find idle rider
        assigned_rider = None
        for rider in self.riders.values():
            if rider["store_id"] == order.assigned_store_id and not rider["is_busy"]:
                assigned_rider = rider
                rider["is_busy"] = True
                break

        if not assigned_rider:
            raise ValueError("No idle delivery rider currently available at this dark store hub.")

        order.assigned_rider_id = assigned_rider["rider_id"]
        order.status = "OUT_FOR_DELIVERY"

        return {
            "order_id": order.order_id,
            "status": order.status,
            "rider_name": assigned_rider["name"],
            "eta_minutes": 10,
            "store": self.stores[order.assigned_store_id].store_name
        }
