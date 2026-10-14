import hashlib

class LinguisticCell:
    """
    CÂY CẦU NÂNG CHIỀU:
    Biến chuỗi chữ viết từ Internet (Wikipedia / Markdown) -> Vector 4 chiều [0.0, 1.0]
    """
    @staticmethod
    def embed_text(text):
        if not text:
            return [0.0, 0.0, 0.0, 0.0]

        clean_text = str(text).strip().lower()
        coords = []
        for d in range(4):
            seed = f"{clean_text}_semantic_axis_{d}".encode()
            val = int(hashlib.shake_256(seed).hexdigest(4), 16) / 65535.0
            coords.append(round(val, 4))

        return coords
