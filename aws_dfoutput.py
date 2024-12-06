import pandas as pd
import json

# Provided JSON string
processed_data = [
    {
        "catalog_id": "1976.pdf",
        "page_num": 4,
        "tabular_data": [
            {"plate_id": "5291", "right_ascension": "8h 4m", "declination": "+21° 32'", "exposure_time": "7:51 – 8:13; 8:14 – 8:36", "seeing_conditions": "Good", "instrument_used": "8x10 103aO", "astronomer": "", "notes": ""},
            {"plate_id": "5294", "right_ascension": "5h 45m", "declination": "-50° 3'", "exposure_time": "8:58 – 9:20; 9:21 – 9:43", "seeing_conditions": "Good", "instrument_used": "5 Oak 8x10 103aO", "astronomer": "", "notes": ""},
            {"plate_id": "5296", "right_ascension": "11h", "declination": "+45° 2'", "exposure_time": "9:58 – 10:20", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "", "notes": "R. Millis"},
            {"plate_id": "5297", "right_ascension": "0h 47m 35.3s", "declination": "-48° 06' 19\"", "exposure_time": "10:21 – 10:43", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "H. L. Giclas", "notes": ""},
            {"plate_id": "5312", "right_ascension": "1h 18m", "declination": "+43° 35'", "exposure_time": "11:00 – 11:22", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "BAS", "notes": ""},
            {"plate_id": "5313", "right_ascension": "0h 29m", "declination": "+43° 35'", "exposure_time": "11:23 – 11:45", "seeing_conditions": "Good", "instrument_used": "HIS 103aO", "astronomer": "MW", "notes": "SA 57"},
            {"plate_id": "5319", "right_ascension": "12h 26m 27s", "declination": "+29° 48'", "exposure_time": "12:00 – 12:22", "seeing_conditions": "Good", "instrument_used": "8x10 103aO", "astronomer": "", "notes": "No E Foid"}
        ],
        "extra_information": "",
        "metadata": {
            "author": "Giclas, Henry; Burnham, Robert; Thomas, Norman; Millis, Bob; Bowell, Ted; ELGB; BAS; MW",
            "date": "1976-04-27",
            "title": "13-inch Observation Logbook, 1976"
        }
    }
]

# Flatten the JSON into rows
rows = []
for entry in processed_data:
    catalog_id = entry["catalog_id"]
    page_num = entry["page_num"]
    metadata = entry["metadata"]
    
    for record in entry["tabular_data"]:
        row = {
            "catalog_id": catalog_id,
            "page_num": page_num,
            "author": metadata["author"],
            "date": metadata["date"],
            "title": metadata["title"],
            **record
        }
        rows.append(row)

# Create a DataFrame
df = pd.DataFrame(rows)
cols = df.columns[2:]
df = df[cols]
# Display the DataFrame
print(df['instrument_used'])

# Save to CSV if needed
# df.to_csv("tabular_data.csv", index=False)
