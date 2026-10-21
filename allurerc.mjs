// Run pytest first, then generate and publish with a project-local Allure 3 CLI:
//   python -m pytest
//   npx allure generate ./temps --config ./allurerc.mjs
// Obtain ALLURE_SERVICE_ACCESS_TOKEN from POST /api/token on the storage service.
const accessToken = "ars1.eyJhY2Nlc3NUb2tlbiI6IldlV1BKOFRiOV9oNzBzVmxjV05GSld3bm1vMkVUbnRyZG1ka3VxQllOZU0iLCJ1cmwiOiJodHRwOi8vMTM0LjE3NS4xMzQuNjQ6MzAwMCJ9.6jiz0pX5yq9tIsoLrj-jZw5lJQW-vZxXtw4NskHgse8";

if (!accessToken?.startsWith("ars1.")) {
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
        publish: process.env.ALLURE_SERVICE_PUBLISH === "true",
      },
    },
  },
  allureService: {
    accessToken,
  },
};
