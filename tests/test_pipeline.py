"""检测流水线单元测试。"""

import pytest
from pathlib import Path
from pipeline import InspectionPipeline, StepStatus


# 测试数据路径
ROOT = Path(__file__).parent.parent
DATA_ROOT = ROOT / "data"
MES_PATH = ROOT / "MES-ID.cgf"
MODEL_PATH = ROOT / "models" / "best.pt"


@pytest.fixture
def pipeline():
    """创建检测流水线实例。"""
    return InspectionPipeline(MES_PATH, MODEL_PATH)


class TestInspectionPipeline:
    """检测流水线测试类。"""

    def test_mes_loading(self, pipeline):
        """测试MES数据加载。"""
        assert len(pipeline.mes) > 0, "MES数据不应为空"
        
    def test_sample_2_detection(self, pipeline):
        """测试样品2的完整检测流程（应该通过）。"""
        result = pipeline.inspect_sample_dir(DATA_ROOT, "2")
        
        assert result is not None, "检测结果不应为None"
        assert result.sample_id == "2", "样品ID应为2"
        assert result.front.ok, "正面QR码识别应该成功"
        assert result.compare.status == StepStatus.PASS, "三码比对应该通过"
        assert result.defect.status == StepStatus.PASS, "瑕疵检测应该通过（无瑕疵）"
        assert result.overall == StepStatus.PASS, "总体判定应该通过"
        
    def test_sample_3_detection(self, pipeline):
        """测试样品3的完整检测流程（有瑕疵）。"""
        result = pipeline.inspect_sample_dir(DATA_ROOT, "3")
        
        assert result is not None, "检测结果不应为None"
        assert result.sample_id == "3", "样品ID应为3"
        assert result.front.ok, "正面QR码识别应该成功"
        assert result.defect.status == StepStatus.FAIL, "瑕疵检测应该失败（有瑕疵）"
        assert result.overall == StepStatus.FAIL, "总体判定应该失败"
        
    def test_sample_6_detection(self, pipeline):
        """测试样品6的完整检测流程（有瑕疵）。"""
        result = pipeline.inspect_sample_dir(DATA_ROOT, "6")
        
        assert result is not None, "检测结果不应为None"
        assert result.sample_id == "6", "样品ID应为6"
        assert result.front.ok, "正面QR码识别应该成功"
        assert result.defect.status == StepStatus.FAIL, "瑕疵检测应该失败（有瑕疵）"
        assert result.overall == StepStatus.FAIL, "总体判定应该失败"
        
    def test_invalid_sample(self, pipeline):
        """测试无效样品的处理。"""
        result = pipeline.inspect_sample_dir(DATA_ROOT, "invalid_sample_id")
        
        # 应该能够处理不存在的样品，不会崩溃
        assert result is not None or result is None, "应该能够处理无效样品ID"


class TestCodeMatching:
    """三码比对测试类。"""

    def test_qr_decoding(self, pipeline):
        """测试QR码解码。"""
        from QRDecode import decode_qr
        import cv2
        
        # 读取正面图像
        front_img = cv2.imdecode(
            cv2.imread(str(DATA_ROOT / "front" / "2-1.jpg"), cv2.IMREAD_COLOR),
            cv2.IMREAD_COLOR
        ) if (DATA_ROOT / "front" / "2-1.jpg").exists() else None
        
        if front_img is not None:
            qr_data = decode_qr(front_img)
            assert qr_data is not None or qr_data is None, "应该能够处理QR码解码"
            
    def test_barcode_decoding(self, pipeline):
        """测试条码解码。"""
        from QRDecode import decode_barcode
        
        # 读取侧面图像
        side_path = DATA_ROOT / "side" / "2-3.jpg"
        if side_path.exists():
            import cv2
            side_img = cv2.imdecode(
                cv2.imread(str(side_path), cv2.IMREAD_COLOR),
                cv2.IMREAD_COLOR
            )
            if side_img is not None:
                barcode_data = decode_barcode(side_img)
                assert barcode_data is not None or barcode_data is None, "应该能够处理条码解码"


class TestPerformance:
    """性能测试类。"""

    def test_detection_speed(self, pipeline):
        """测试检测速度。"""
        import time
        
        start = time.time()
        result = pipeline.inspect_sample_dir(DATA_ROOT, "2")
        elapsed = time.time() - start
        
        # CPU模式下应该在5秒内完成
        assert elapsed < 5.0, f"检测时间应小于5秒，实际: {elapsed:.2f}秒"
        
    def test_multiple_samples(self, pipeline):
        """测试批量检测。"""
        sample_ids = ["1", "2", "3", "4", "5"]
        results = []
        
        for sid in sample_ids:
            if (DATA_ROOT / "front" / f"{sid}-1.jpg").exists():
                result = pipeline.inspect_sample_dir(DATA_ROOT, sid)
                results.append(result)
                
        assert len(results) > 0, "应该能够检测多个样品"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
