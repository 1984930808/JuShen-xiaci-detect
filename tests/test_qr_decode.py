"""QR码和条码解码测试。"""

import pytest
import cv2
from pathlib import Path
from QRDecode import decode_qr, decode_barcode, imread_unicode


ROOT = Path(__file__).parent.parent
DATA_ROOT = ROOT / "data"


class TestQRDecode:
    """QR码解码测试类。"""

    def test_decode_qr_from_sample_2(self):
        """测试从样品2解码QR码。"""
        front_path = DATA_ROOT / "front" / "2-1.jpg"
        if not front_path.exists():
            pytest.skip("样品2正面图像不存在")
            
        img = imread_unicode(front_path)
        assert img is not None, "应该能够读取图像"
        
        qr_data = decode_qr(img)
        assert qr_data is not None, "应该能够解码QR码"
        assert len(qr_data) > 0, "QR码内容不应为空"
        
    def test_decode_qr_from_multiple_samples(self):
        """测试从多个样品解码QR码。"""
        success_count = 0
        
        for i in range(1, 11):
            front_path = DATA_ROOT / "front" / f"{i}-1.jpg"
            if front_path.exists():
                img = imread_unicode(front_path)
                if img is not None:
                    qr_data = decode_qr(img)
                    if qr_data:
                        success_count += 1
                        
        assert success_count >= 8, f"至少应该成功解码8个样品的QR码，实际: {success_count}"


class TestBarcodeDecode:
    """条码解码测试类。"""

    def test_decode_barcode_from_sample_2(self):
        """测试从样品2解码条码。"""
        side_path = DATA_ROOT / "side" / "2-3.jpg"
        if not side_path.exists():
            pytest.skip("样品2侧面图像不存在")
            
        img = imread_unicode(side_path)
        assert img is not None, "应该能够读取图像"
        
        barcode_data = decode_barcode(img)
        assert barcode_data is not None, "应该能够解码条码"
        assert len(barcode_data) > 0, "条码内容不应为空"
        
    def test_decode_barcode_from_multiple_samples(self):
        """测试从多个样品解码条码。"""
        success_count = 0
        
        for i in range(1, 11):
            side_path = DATA_ROOT / "side" / f"{i}-3.jpg"
            if side_path.exists():
                img = imread_unicode(side_path)
                if img is not None:
                    barcode_data = decode_barcode(img)
                    if barcode_data:
                        success_count += 1
                        
        assert success_count >= 8, f"至少应该成功解码8个样品的条码，实际: {success_count}"


class TestImageReading:
    """图像读取测试类。"""

    def test_imread_unicode_with_chinese_path(self):
        """测试中文路径图像读取。"""
        # 测试项目中的图像读取
        front_path = DATA_ROOT / "front" / "1-1.jpg"
        if not front_path.exists():
            pytest.skip("测试图像不存在")
            
        img = imread_unicode(front_path)
        assert img is not None, "应该能够读取中文路径的图像"
        assert len(img.shape) == 3, "图像应该是三通道"
        
    def test_imread_unicode_with_invalid_path(self):
        """测试无效路径处理。"""
        img = imread_unicode("nonexistent_path.jpg")
        assert img is None, "无效路径应该返回None"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
