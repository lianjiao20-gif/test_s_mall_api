// Run pytest first, then generate and publish with a project-local Allure 3 CLI:
//   python -m pytest
//   npx allure generate ./temps --config ./allurerc.mjs
// Obtain ALLURE_SERVICE_ACCESS_TOKEN from POST /api/token on the storage service.
import { existsSync } from "node:fs";
import { loadEnvFile } from "node:process";

if (existsSync(".env")) {
  loadEnvFile(".env");
}

const publish = process.env.ALLURE_SERVICE_PUBLISH === "true";
const accessToken = process.env.ALLURE_SERVICE_ACCESS_TOKEN;
if (publish && !accessToken?.startsWith("ars1.")) {
  throw new Error(
    "Set ALLURE_SERVICE_ACCESS_TOKEN to the ars1. report token issued by Allure Report Storage",
  );
}

export default {
  name: "商城 API 自动化测试",
  output: "./reports",
  plugins: {
    awesome: {
      options: {
        publish,
      },
    },
  },
  ...(publish ? { allureService: { accessToken } } : {}),
};
