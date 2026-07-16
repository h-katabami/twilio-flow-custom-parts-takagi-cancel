import csv
import io


def build_csv_bytes(rows, fieldnames, encoding="utf-8-sig", include_header=True):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")

    if include_header:
        writer.writeheader()

    for row in rows:
        writer.writerow(
            {
                fieldname: "" if row.get(fieldname) is None else str(row.get(fieldname))
                for fieldname in fieldnames
            }
        )

    return output.getvalue().encode(encoding, errors="replace")
