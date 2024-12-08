import sqlite3
from datetime import datetime
import binascii
import re

def decode_attributed_body(attributed_body):
    if attributed_body is None:
        return None
    
    try:
        # Convert to hex string
        hex_string = attributed_body.hex()
        
        # Decode hex to bytes
        attributed_body_bytes = binascii.unhexlify(hex_string)
        
        # Decode as UTF-8 and extract readable text
        decoded_text = attributed_body_bytes.decode('utf-8', errors='ignore')
        readable_text = re.findall(r'[\x20-\x7E]+', decoded_text)
        return ' '.join(readable_text)
    except Exception as e:
        return f"Error decoding attributedBody: {e}"

# Connect to the database
conn = sqlite3.connect("path/to/chat.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Set the date range
start_date = datetime(2024, 12, 1)
end_date = datetime(2024, 12, 7)  # Today's date

# Convert dates to Unix timestamp (seconds since 1970-01-01)
start_timestamp = int((start_date - datetime(2001, 1, 1)).total_seconds() * 1000000000)
end_timestamp = int((end_date - datetime(2001, 1, 1)).total_seconds() * 1000000000)

query = """
SELECT
    datetime (message.date / 1000000000 + strftime ("%s", "2001-01-01"), "unixepoch", "localtime") AS message_date,
    message.text,
    message.attributedBody,
    message.is_from_me,
    chat.chat_identifier
FROM
    chat
    JOIN chat_message_join ON chat. "ROWID" = chat_message_join.chat_id
    JOIN message ON chat_message_join.message_id = message. "ROWID"
WHERE 
    message.date BETWEEN ? AND ?
ORDER BY
    message_date DESC;
"""

cursor.execute(query, (start_timestamp, end_timestamp))

for row in cursor:
    message_date = row['message_date']
    text = row['text']
    attributed_body = row['attributedBody']
    is_from_me = row['is_from_me']
    chat_identifier = row['chat_identifier']
    
    if text is None and attributed_body is not None:
        decoded_text = decode_attributed_body(attributed_body)
    else:
        decoded_text = text
    
    print(f"Date: {message_date}")
    print(f"Message: {decoded_text}")
    print(f"From me: {'Yes' if is_from_me else 'No'}")
    print(f"Chat: {chat_identifier}")
    print("---")

conn.close()

