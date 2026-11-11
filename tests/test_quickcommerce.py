import unittest
from quickcommerce.engine import QuickCommerceEngine, DarkStore, QuickOrderItem


class TestQuickCommerceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = QuickCommerceEngine()
        # Indiranagar Bangalore Dark Store
        self.store = DarkStore(
            store_id="DS-BLR-01",
            store_name="Indiranagar Dark Store Hub",
            latitude=12.9719,
            longitude=77.6412,
            max_delivery_radius_km=3.0,
            inventory={"MILK-1L": 50, "BREAD-WHITE": 30, "EGGS-6PK": 40}
        )
        self.engine.register_dark_store(self.store)
        self.engine.add_rider("R-101", "Kiran Kumar", "DS-BLR-01")

    def test_serviceable_order_and_inventory_deduction(self):
        # Customer is 1.5 km away (12.9780, 77.6450)
        items = [
            QuickOrderItem(sku="MILK-1L", quantity=2, unit_price=35.0),
            QuickOrderItem(sku="EGGS-6PK", quantity=1, unit_price=60.0)
        ]
        order = self.engine.place_quick_order(
            customer_id="CUST-881",
            customer_lat=12.9780,
            customer_lon=77.6450,
            items=items
        )
        self.assertEqual(order.assigned_store_id, "DS-BLR-01")
        self.assertEqual(order.total_amount, 130.0)
        self.assertEqual(self.store.inventory["MILK-1L"], 48)  # 50 - 2
        self.assertEqual(self.store.inventory["EGGS-6PK"], 39)  # 40 - 1

        # Dispatch order to rider
        dispatch = self.engine.dispatch_order(order.order_id)
        self.assertEqual(dispatch["status"], "OUT_FOR_DELIVERY")
        self.assertEqual(dispatch["rider_name"], "Kiran Kumar")

    def test_out_of_radius_fails(self):
        # Customer 15 km away in Electronic City (12.8452, 77.6602)
        items = [QuickOrderItem(sku="MILK-1L", quantity=1, unit_price=35.0)]
        with self.assertRaises(ValueError):
            self.engine.place_quick_order(
                customer_id="CUST-999",
                customer_lat=12.8452,
                customer_lon=77.6602,
                items=items
            )


if __name__ == "__main__":
    unittest.main()
