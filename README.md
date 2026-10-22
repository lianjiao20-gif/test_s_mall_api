# 商城 API 自动化测试

基于 `pytest`、`requests` 和 YAML 测试数据的商城接口测试项目。用例覆盖健康检查、登录与用户信息、商品、购物车和订单接口；断言由 `commons/assert_util.py` 统一处理。`make test-only` 生成本地 Allure 报告，`make test` 还会将报告发布到 Allure Report Storage。

## 环境要求

- Python 3.11（当前项目使用的版本）
- 可访问测试接口的网络环境
- `make` 和 Allure Report 3 命令行工具；运行 `allure --version` 应显示 3.x
- 发布报告时，本机还需能访问 Allure Report Storage 服务

`requirements.txt` 包含 pytest、Allure pytest 插件、PyYAML 等依赖；`requests` 由 `pytest-base-url` 的依赖一并安装。

## 快速开始

在项目根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
make install

cp data/login/test_login.example.yaml data/login/test_login.yaml
cp data/login/test_get_user.example.yaml data/login/test_get_user.yaml
```

随后编辑这两个本地 YAML 文件，填入专用测试账号、接口地址及对应的预期结果。示例文件仅提供格式参考，不包含可直接使用的账号。**即使只运行健康检查，也要先创建这两个文件**：pytest 在收集用例时会读取它们。

`make install` 只安装 Python 依赖。Allure Report 3 需要单独安装，并确保 `allure` 命令指向 3.x；例如已安装 Node.js 和 npm 时，可运行 `npm install -g allure`。

项目中的其他 YAML 用例目前使用完整接口 URL；切换测试环境时，需要同步修改这些 URL。`pytest.ini` 中的 `base_url` 不会自动替换 YAML 里的完整 URL。请从项目根目录运行命令，因为代码按相对路径读取测试数据。

## 运行测试

```bash
# 运行全部用例，并在 reports/ 生成本地 HTML 报告；默认不上传
make test-only

# 运行全部用例、生成报告，并发布到 Allure Report Storage
make test

# 仅运行指定用例：只写入 temps/，不会生成 HTML 报告或上传
python -m pytest -m smoke
python -m pytest testcases/products/test_products.py
```

`pytest.ini` 默认开启 `--alluredir=./temps --clean-alluredir`，每次运行都会清理上一次的原始结果。两个 Make 目标都会在 pytest 通过或仅有用例失败时生成报告；如果用例失败，`make` 最终仍返回失败状态。购物车和订单用例可能创建或修改测试数据，建议使用专用测试环境和账号。

查看本地报告：

```bash
allure open ./reports
```

### 发布报告的令牌

`make test` 会设置 `ALLURE_SERVICE_PUBLISH=true`，`allurerc.mjs` 因此使用项目根目录 `.env` 中的报告访问令牌。先用部署 Allure Report Storage 时设置的 **bootstrap `ACCESS_TOKEN`** 签发令牌：

```bash
curl -X POST 'http://<storage-host>:3000/api/token' \
  -H 'Authorization: Bearer <bootstrap ACCESS_TOKEN>'
```

取得 `ars1.` 开头的令牌后，在项目根目录创建 `.env`：

```dotenv
ALLURE_SERVICE_ACCESS_TOKEN=ars1.替换为签发的报告访问令牌
```

`make test-only` 默认不发布，也不要求令牌。不要在 `.env` 或当前 shell 中设置 `ALLURE_SERVICE_PUBLISH=true`，否则它也会尝试发布。`.env` 已被 Git 忽略，不要将真实令牌写入 README 或提交到仓库。此发布流程连接的是 **Allure Report Storage**，不是 Allure Docker Service UI。

## 项目结构

```text
commons/                  请求、YAML 读取和断言工具
data/                     接口测试数据（YAML）
  login/                  登录与用户信息；本地账号文件不提交
  products/               商品用例
  shopcart/               购物车用例
  order/                  订单用例
testcases/                pytest 测试代码与登录 token fixture
pytest.ini                pytest 配置与冒烟标记
makefile                  本地报告与发布报告的运行入口
allurerc.mjs              Allure 3 报告及发布配置
.env                      本地报告访问令牌（不提交）
run.py                    旧的测试及报告生成入口；建议使用 make
temps/                   Allure 原始结果（运行时生成）
reports/                 Allure HTML 报告（运行时生成）
extract.yaml             登录后生成的 token（运行时生成）
```

## 测试数据与断言

测试方法通过 `pytest.mark.parametrize` 加载对应的 YAML 文件。一个用例通常包含 `request` 和 `validate`：

```yaml
- feature: 健康检查模块
  story: 健康检查接口
  title: 验证成功
  request:
    methods: get
    url: https://your-test-api.example/api/health
    headers: null
  validate:
    - eq: ["status_code", 200]
    - eq: ["json.status", "ok"]
```

`validate` 支持 `eq`、`ne`、`gt`、`lt`、`contains` 和 `len_eq`。取值路径可使用 `status_code`、`text` 或 `json.字段.子字段`。需要认证的用例在请求头中使用 `Bearer ${token}`；会话级 `auth_token` fixture 从本地登录 YAML 找到带 `extract` 的用例，登录后将 token 注入请求头。

## 本地数据与 Git

`.gitignore` 忽略 `data/login/test_login.yaml`、`data/login/test_get_user.yaml`、`.env`、运行时的 `extract.yaml`、虚拟环境、缓存及 Allure 生成目录。仓库只保留 `*.example.yaml` 模板；不要把真实账号、密码或 token 写入这些模板。

如果敏感文件在设置忽略规则前已经被 Git 跟踪，`.gitignore` 不会自动取消跟踪；需要单独从 Git 索引移除，并检查是否已推送到远端。

## 部分allure截图

![alt text](asset/image-1.png)
![alt text](asset/image.png)
![alt text](asset/image-2.png)
