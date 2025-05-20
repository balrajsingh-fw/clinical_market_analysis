from analysis.models import DrugSale
import random

asian_city_coordinates = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Beijing": (39.9042, 116.4074),
    "Shanghai": (31.2304, 121.4737),
    "Tokyo": (35.6895, 139.6917),
    "Seoul": (37.5665, 126.9780),
    "Jakarta": (-6.2088, 106.8456),
    "Manila": (14.5995, 120.9842),
    "Karachi": (24.8607, 67.0011),
    "Dhaka": (23.8103, 90.4125),
    "Hanoi": (21.0285, 105.8542),
    "Bangkok": (13.7563, 100.5018),
    "Kuala Lumpur": (3.1390, 101.6869),
    "Singapore": (1.3521, 103.8198),
    "Colombo": (6.9271, 79.8612),
    "Kathmandu": (27.7172, 85.3240),
    "Yangon": (16.8409, 96.1735),
    "Riyadh": (24.7136, 46.6753),
    "Dubai": (25.2048, 55.2708),
    "Tehran": (35.6892, 51.3890),
    "Istanbul": (40.9900, 29.0290),
    "Kabul": (34.5553, 69.2075),
}

cities = list(asian_city_coordinates.keys())


def assign_locations_to_drugs():
    sales = DrugSale.objects.all()
    for sale in sales:
        city = random.choice(cities)
        lat, lon = asian_city_coordinates[city]

        sale.city = city
        sale.latitude = lat
        sale.longitude = lon
        sale.save()

    print(f"Assigned coordinates to {sales.count()} records.")


assign_locations_to_drugs()
