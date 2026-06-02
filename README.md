# scenic-dh-business-api

智慧景区数字人平台 — 业务域接口服务。

## 快速开始

```bash
cd scenic-dh-business-api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

健康检查: http://localhost:8001/health
API 文档: http://localhost:8001/docs

## 已实现端点

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | /health | 健康检查 | ✅ |
| GET | /v1/scenic-areas/{id} | 景区基础资料 | ✅ |
| GET | /v1/spots | 景点列表（分页/搜索） | ✅ |
| GET | /v1/spots/{id} | 景点详情 | ✅ |
| GET | /v1/spots/{id}/guide | 景点讲解词 | ✅ |
| GET | /v1/routes | 路线列表 | ✅ |
| GET | /v1/routes/{id} | 路线详情 | ✅ |
| POST | /v1/routes/plan | 路线规划 | ✅ |
| POST | /v1/sessions | 创建会话 | ✅ |
| GET | /v1/sessions/{id} | 查询会话 | ✅ |
| PATCH | /v1/sessions/{id} | 更新会话 | ✅ |
| POST | /v1/sessions/{id}/messages | 记录消息 | ✅ |
| GET | /v1/sessions/{id}/messages | 查询消息 | ✅ |
| POST | /v1/sessions/{id}/arrival-events | 到达事件 | ✅ |
| GET | /v1/sessions/{id}/arrival-events | 查询到达 | ✅ |
| POST | /v1/sessions/{id}/feedback | 提交反馈 | ✅ |
| GET | /v1/feedback | 反馈列表 | ✅ |
| GET | /v1/notices | 公告列表 | ✅ |
| GET | /v1/events | 活动列表 | ✅ |
| GET | /v1/services | 服务设施 | ✅ |
| GET | /v1/weather | 天气（mock） | ✅ |
| GET | /v1/queues | 排队（mock） | ✅ |
| GET | /v1/tickets/products | 票务（mock） | ✅ |
| GET | /v1/analytics/visitor-behavior | 游客行为 | ✅ |

## 待实现

- [ ] POST /internal/v1/context/query — 编排层上下文查询
- [ ] POST /internal/v1/seed/public-package — 资料包导入
- [ ] 资料来源标记统一化
- [ ] SQLite 持久化（当前内存存储）
- [ ] 内部服务 token 校验
- [ ] admin-api
- [ ] demo-mock-service

## 契约

所有响应格式对齐 `scenic-dh-contracts`。
