"""MES数据库测试。"""

import pytest
from pathlib import Path
from mes_db import MesDatabase, MesRecord


ROOT = Path(__file__).parent.parent
MES_PATH = ROOT / "MES-ID.cgf"


@pytest.fixture
def mes_db():
    """创建MES数据库实例。"""
    return MesDatabase(MES_PATH)


class TestMESDatabase:
    """MES数据库测试类。"""

    def test_mes_loading(self, mes_db):
        """测试MES数据加载。"""
        assert len(mes_db) > 0, "MES记录不应为空"
        
    def test_lookup_by_qr(self, mes_db):
        """测试通过QR码查询。"""
        # 测试样品2的QR码（根据实际MES数据调整）
        # 遍历所有记录找到第一个进行测试
        for qr_code in mes_db._by_qr.keys():
            record = mes_db.lookup_by_qr(qr_code)
            if record:
                assert record.qr_code is not None, "QR码不应为空"
                assert record.barcode is not None, "条码不应为空"
                assert isinstance(record.defect_free, bool), "瑕疵标记应为布尔值"
                break
            
    def test_lookup_invalid_qr(self, mes_db):
        """测试查询无效QR码。"""
        record = mes_db.lookup_by_qr("INVALID_QR_CODE_12345")
        assert record is None, "无效QR码应该返回None"
        
    def test_all_records_have_required_fields(self, mes_db):
        """测试所有记录都有必需字段。"""
        for qr_code, record in mes_db._by_qr.items():
            assert record.qr_code is not None, f"QR码不应为空: {qr_code}"
            assert record.barcode is not None, f"条码不应为空: {qr_code}"
            assert record.defect_free is not None, f"瑕疵标记不应为空: {qr_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
