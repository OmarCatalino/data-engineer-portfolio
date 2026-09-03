import csv

input_path = "diagnostics/data/orders.csv"
output_path = "diagnostics/data/filtered_orders.csv"

filtered_rows = []
kept = 0
dropped = 0

with open(input_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        status = row["status"].strip().lower()
        quantity_str = row["quantity"].strip()

        if status == "cancelled" or quantity_str == "":
            dropped += 1
            continue

        quantity = int(quantity_str)
        price = float(row["price"])
        row["total_price"] = round(quantity * price, 2)

        filtered_rows.append(row)
        kept += 1

fieldnames = ["order_id", "customer_name", "product", "quantity", "price", "order_date", "status", "total_price"]

with open(output_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in filtered_rows:
        writer.writerow(row)

print(f"Kept: {kept} rows")
print(f"Dropped: {dropped} rows")
print(f"Output written to {output_path}")