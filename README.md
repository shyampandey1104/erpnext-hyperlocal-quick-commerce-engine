# ERPNext Hyperlocal Quick Commerce & Dark Store Engine ⚡🛒

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![ERPNext](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

An enterprise hyperlocal quick-commerce dark store fulfillment, geofenced micro-warehouse routing, and 10-minute dispatch engine for **ERPNext & Frappe Framework** (Blinkit, Zepto, Instamart architecture).

---

## 🚀 Key Features

- **Haversine Geofencing Radius**: Automatically allocates orders to dark stores strictly within 2.5 - 3.5 km delivery boundaries.
- **Sub-Second Inventory Lock**: Atomically locks and decrements micro-warehouse SKUs to prevent out-of-stock cancellations.
- **Picker-Packer Batch Routing**: Optimizes item retrieval paths inside micro-fulfillment centers.
- **Idle Rider Dispatch**: Instantly couples packed order bags with available hub riders for under-10-minute turnaround.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/erpnext-hyperlocal-quick-commerce-engine.git
cd erpnext-hyperlocal-quick-commerce-engine
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from quickcommerce.engine import QuickCommerceEngine, DarkStore, QuickOrderItem

engine = QuickCommerceEngine()

store = DarkStore(
    store_id="DS-01",
    store_name="Koramangala Hub",
    latitude=12.9352,
    longitude=77.6245,
    max_delivery_radius_km=3.0,
    inventory={"AMUL-BUTTER-500G": 20, "WHOLE-WHEAT-BREAD": 15}
)
engine.register_dark_store(store)
engine.add_rider("R-1", "Sanjay", "DS-01")

# Customer places 10-minute order
order = engine.place_quick_order(
    customer_id="CUST-42",
    customer_lat=12.9390,
    customer_lon=77.6280,
    items=[QuickOrderItem(sku="AMUL-BUTTER-500G", quantity=1, unit_price=275.0)]
)

dispatch = engine.dispatch_order(order.order_id)
print(f"Order {order.order_id} assigned to Rider {dispatch['rider_name']}. ETA: {dispatch['eta_minutes']} mins.")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
