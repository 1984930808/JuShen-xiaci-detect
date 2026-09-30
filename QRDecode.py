import cv2
from pyzbar.pyzbar import decode
import numpy as np


def imread_unicode(path):
    """读取含中文路径的图片（OpenCV 原生 imread 在 Windows 下会失败）。"""
    data = np.fromfile(str(path), dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def qr_frame_decode(frame):
    """解码图像中的二维码/条码，返回类型、内容、位置列表。"""
    grayimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.uint8(np.clip((1.1 * grayimg + 10), 0, 255))
    objects = decode(gray)

    height, width = frame.shape[:2]
    scale = 1.0
    if width > 1280:
        scale = width / 1280

    tps = []
    datas = []
    positons = []

    for obj in objects:
        data = obj.data.decode("utf-8")
        (x, y, w, h) = obj.rect
        (x, y, w, h) = (int(x / scale), int(y / scale), int(w / scale), int(h / scale))

        tps.append(obj.type)
        datas.append(data)
        positons.append([x, y, w, h])

    return tps, datas, positons


def decode_preferred(frame, preferred_types=("QRCODE",)):
    """
    按优先类型解码。
    - preferred_types: 优先返回的码类型（正面 QRCODE，侧面/背面 CODE128）
    返回 (data, type, position) 或 (None, None, None)
    """
    candidates = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    variants = [
        gray,
        np.uint8(np.clip((1.1 * gray + 10), 0, 255)),
        cv2.equalizeHist(gray),
    ]
    h, w = gray.shape[:2]
    if max(h, w) < 800:
        variants.append(
            cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        )

    for img in variants:
        for obj in decode(img):
            data = obj.data.decode("utf-8")
            (x, y, bw, bh) = obj.rect
            candidates.append((obj.type, data, [x, y, bw, bh]))

    if not candidates:
        return None, None, None

    preferred = {t.upper() for t in preferred_types}
    for tp, data, pos in candidates:
        if tp.upper() in preferred:
            return data, tp, pos

    tp, data, pos = candidates[0]
    return data, tp, pos


def annotate_code(frame, data, position, color=(0, 220, 0)):
    """在图上画出码框与文字，返回副本。"""
    out = frame.copy()
    if position is None:
        return out
    x, y, w, h = position
    cv2.rectangle(out, (x, y), (x + w, y + h), color, 2)
    label = data or ""
    cv2.putText(out, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return out
