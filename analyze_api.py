
import re
import json

# 读取文件
with open('/workspace/index.js', 'r', encoding='utf-8') as f:
    index_content = f.read()

with open('/workspace/register.js', 'r', encoding='utf-8') as f:
    register_content = f.read()

with open('/workspace/vendors.js', 'r', encoding='utf-8') as f:
    vendors_content = f.read()

print("=" * 80)
print("搜索 API 相关关键词")
print("=" * 80)

# 搜索关键词
keywords = [
    r'https?://[^\s"\']+',  # URL
    r'api/[^\s"\']+',        # API路径
    r'getConfig',             # 获取配置
    r'sendSms',               # 发送短信
    r'register',              # 注册
    r'login',                 # 登录
    r'captcha',               # 验证码
    r'password',              # 密码
    r'mobile',                # 手机号
    r'invite',                # 邀请
]

all_content = index_content + register_content + vendors_content

for keyword in keywords:
    matches = re.findall(keyword, all_content)
    if matches:
        print(f"\n关键词: {keyword}")
        print("-" * 40)
        # 去重并显示
        unique_matches = list(set(matches))[:20]  # 最多显示20个
        for match in unique_matches:
            print(f"  {match}")

print("\n" + "=" * 80)
print("搜索可能的 API 端点模式")
print("=" * 80)

# 搜索可能的API端点
api_patterns = [
    r'["\']([^"\']*api[^"\']*)["\']',
    r'["\'](/[^"\']*register[^"\']*)["\']',
    r'["\'](/[^"\']*login[^"\']*)["\']',
    r'["\'](/[^"\']*sms[^"\']*)["\']',
    r'["\'](/[^"\']*captcha[^"\']*)["\']',
]

for pattern in api_patterns:
    matches = re.findall(pattern, all_content)
    if matches:
        print(f"\n模式: {pattern}")
        print("-" * 40)
        unique_matches = list(set(matches))
        for match in unique_matches:
            print(f"  {match}")

print("\n" + "=" * 80)
print("搜索域名相关")
print("=" * 80)

# 搜索域名
domain_patterns = [
    r'www\.wanhouart\.top',
    r'h5\.alt\.wanhouart\.top',
    r'wanhouart\.top',
]

for pattern in domain_patterns:
    matches = re.findall(pattern, all_content)
    if matches:
        print(f"\n域名: {pattern}")
        print(f"出现次数: {len(matches)}")

# 尝试查找完整的API URL
full_url_pattern = r'https?://[^\s"\'{}]+'
full_urls = re.findall(full_url_pattern, all_content)
if full_urls:
    print("\n" + "=" * 80)
    print("找到的所有URL")
    print("=" * 80)
    unique_urls = list(set(full_urls))
    for url in sorted(unique_urls):
        print(url)

