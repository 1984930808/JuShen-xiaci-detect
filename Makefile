# Makefile for JuShen Defect Detection System

.PHONY: help install test clean run train

help:
	@echo "JuShen 瑕疵检测系统 - 可用命令:"
	@echo "  make install    - 安装依赖"
	@echo "  make install-dev- 安装开发依赖"
	@echo "  make run        - 运行检测软件"
	@echo "  make test       - 运行单元测试"
	@echo "  make test-cov   - 运行测试并生成覆盖率报告"
	@echo "  make train      - 训练模型"
	@echo "  make clean      - 清理临时文件"
	@echo "  make lint       - 代码检查"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

run:
	python app.py

test:
	python scripts/run_tests.py

test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term
	@echo "覆盖率报告已生成: htmlcov/index.html"

train:
	python train.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "*.pyc" -delete

lint:
	flake8 *.py --max-line-length=120
	black --check *.py
	mypy *.py --ignore-missing-imports
