import csv
from io import StringIO


def format_csv(*rows, encoding="utf-8") -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    for row in rows:
        writer.writerow([str(field) if field is not None else "" for field in row])
    return buffer.getvalue().encode(encoding)
