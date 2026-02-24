# LinkedIn AdCP Sales Agent

AdCP Sales Agent，把 AdCP 协议 task 翻译成 LinkedIn Marketing API 调用。

## 结构

```
linkedin-salesagent/
├── src/
│   ├── server.py              # MCP server 入口
│   ├── auth/oauth.py          # LinkedIn OAuth2
│   ├── tasks/
│   │   ├── validate_account.py
│   │   ├── list_creative_formats.py
│   │   ├── create_media_buy.py
│   │   ├── sync_creatives.py
│   │   └── get_delivery.py
│   ├── linkedin/client.py     # LinkedIn API 封装
│   └── models/mappings.py     # AdCP ↔ LinkedIn 数据映射
├── .well-known/agent-card.json
├── .env.template
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.template .env
# 填入 LinkedIn OAuth 凭证

# 3. 启动 MCP server
python -m src.server
```

## MCP Tools

| Tool | 对应 AdCP Task | 说明 |
|------|---------------|------|
| `validate_ad_account` | validate_account | 校验 OAuth token + Ad Account 权限 |
| `list_formats` | list_creative_formats | 返回支持的广告格式 |
| `create_media_buy` | create_media_buy | 创建 Campaign Group + Campaign |
| `sync_creatives` | sync_creatives | 上传素材到 Campaign |
| `get_media_buy_delivery` | get_media_buy_delivery | 拉取投放数据 |
| `get_auth_url` | — | 获取 OAuth 授权 URL |
| `exchange_auth_code` | — | 用授权码换 access token |

## OAuth 流程

1. 调用 `get_auth_url` 获取授权链接
2. 浏览器访问，登录 LinkedIn 授权
3. 拿到 redirect 中的 code，调用 `exchange_auth_code`
4. 把返回的 access_token 写入 .env

## MVP 限制

- 只支持 Single Image Ad
- 受众定位用最简配置（地域 + 语言）
- 不处理审核状态轮询
- 不支持本地图片上传（只接受 URL）
