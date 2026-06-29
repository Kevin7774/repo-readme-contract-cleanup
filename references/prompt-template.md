# Reusable Code-Agent Prompt Template

Use this prompt when asking a code agent to prepare a repository for README/API/deployment documentation cleanup.

```text
你现在不要先写 README，也不要做大规模架构重构。

请先执行一次“README 前置工程治理”，目标是在正式更新 README 前，把仓库里的旧代码、旧配置、旧 API、旧部署说明、旧环境变量、假数据、mock 误用、硬编码、死代码、废弃脚本全部识别出来，并且只删除已经确认废弃的内容。

当前原则：
1. 不重写核心业务逻辑。
2. 不做大规模架构重构。
3. 不随意重命名 API。
4. 不改数据库结构，除非测试或代码证明当前结构有明确错误。
5. 不删除测试夹具里的 mock/fake，只删除生产路径里的假数据、假成功、旧逻辑。
6. 不确定是否废弃的内容，不要删除，列入“疑似废弃，需要人工确认”。
7. 所有删除必须有证据：无引用、无路由入口、无前端调用、无部署入口、无测试依赖、无配置入口。
8. 本轮目标是让仓库状态清晰、可文档化、可部署，不是追求完美重构。

请按步骤执行：

一、输出当前工作树状态：
- git status --short
- git diff --stat
- git diff --name-only

二、建立四张真实工程清单：
1. 功能模块清单
2. API 清单
3. 环境变量清单
4. 开发/生产部署拓扑清单

三、扫描并分类：
- 旧端口和旧拓扑
- 旧 API
- 旧环境变量
- 旧部署配置
- 生产路径中的 fake/mock/demo/placeholder/dummy
- 硬编码域名、ip、端口、绝对路径
- 无引用脚本、无入口代码、过期文档

四、只执行最小修复：
- 删除确认废弃内容
- 修正与当前部署冲突的配置
- 修正 env example
- 修正 ci/compose/nginx/deploy 合约
- 增加必要 smoke/contract test

五、不要执行：
- 不拆大文件
- 不重写核心业务流程
- 不重构数据库
- 不重写前端页面
- 不删除不确定是否仍在使用的脚本

六、验证：
请运行或说明无法运行原因：
- 前端 install/build/test/lint
- 后端 compile/test
- health check
- compose config
- nginx config check 如本机支持

七、最终输出：
## README 前置工程治理报告

### 1. 当前仓库是否适合开始重写 README
### 2. 已确认保留的功能模块
### 3. 已确认保留的 API
### 4. 已确认保留的部署方式
### 5. 已删除的废弃内容
### 6. 已修复的不一致内容
### 7. 疑似废弃但未删除
### 8. 当前不建议在 README 前做的大重构
### 9. 验收结果
### 10. 下一步 README 重写建议
```
