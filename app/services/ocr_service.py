import re
from datetime import datetime

from PIL import Image
import pytesseract


class OCRService:
    def extract_receipt(self, file_storage) -> dict:
        image = Image.open(file_storage.stream)
        text = pytesseract.image_to_string(image)
        return self.parse_text(text)

    def parse_text(self, text: str) -> dict:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        merchant = lines[0] if lines else "Receipt Merchant"
        amounts = []
        for match in re.finditer(r"(?:rp\s*)?([0-9][0-9.,]{3,})", text, re.IGNORECASE):
            amount = match.group(1).replace(".", "").replace(",", "")
            try:
                amounts.append(int(amount) * 100)
            except ValueError:
                continue
        date_match = re.search(r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
        date_value = datetime.utcnow().date()
        if date_match:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
                try:
                    date_value = datetime.strptime(date_match.group(1), fmt).date()
                    break
                except ValueError:
                    pass
        return {
            "merchant": merchant[:160],
            "amount_cents": max(amounts) if amounts else 0,
            "occurred_on": date_value.isoformat(),
            "raw_text": text,
        }

