# ---------- 伪目标（避免与同名文件冲突）----------
.PHONY: test test-only install

test-only: ## 运行测试并生成allure报告，不上传服务器
	@pytest --alluredir=./temps; \
	status=$$?; \
	if [ $$status -eq 0 ] || [ $$status -eq 1 ]; then \
		allure generate ./temps -o ./reports --clean; \
	fi; \
	exit $$status

test: ## 运行测试并生成allure报告，上传服务器, 需要在环境变量中设置ALLURE_SERVICE_PUBLISH=true
	@export ALLURE_SERVICE_PUBLISH=true; \
	pytest --alluredir=./temps; \
	status=$$?; \
	report_status=0; \
	if [ $$status -eq 0 ] || [ $$status -eq 1 ]; then \
		allure generate ./temps --config ./allurerc.mjs --clean || { \
			report_status=$$?; \
			echo 'Allure publication failed; generating a local report for the CI artifact.' >&2; \
			ALLURE_SERVICE_PUBLISH=false allure generate ./temps --config ./allurerc.mjs --clean || true; \
		}; \
	fi; \
	if [ $$report_status -ne 0 ]; then exit $$report_status; fi; \
	exit $$status

install:  ## 安装生产依赖
	pip install --upgrade pip
	pip install -r requirements.txt
