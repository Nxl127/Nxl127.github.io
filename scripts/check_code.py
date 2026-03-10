import os, sys, re, glob, requests

print("🔍 开始运行代码检查器...")

API_KEY = os.getenv("LLM_API_KEY")
if not API_KEY:
    print("❌ 错误：未设置 LLM_API_KEY 环境变量")
    print("💡 请前往 GitHub Settings -> Secrets and variables -> Actions 添加 LLM_API_KEY")
    sys.exit(1)

print(f"✅ API_KEY 已加载（长度：{len(API_KEY)}）")

def check_single_block(lang, code):
    if lang.lower() in ['text', 'plaintext', 'txt']:
        return True, "跳过纯文本"
    
    prompt = f"检查以下{lang}代码是否有明显错误（语法错误、逻辑漏洞等）。如果没有错误，请只回复‘通过’；如果有错误，请简要说明。代码:\n{code}"
    
    try:
        resp = requests.post("https://api.siliconflow.cn/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-Coder-32B-Instruct", "messages": [{"role": "user", "content": prompt}]},
            timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()["choices"][0]["message"]["content"].strip().lower()
            passed = "通过" in result or "没问题" in result
            return passed, result
        else:
            return False, f"API错误：{resp.status_code} - {resp.text}"
    except Exception as e:
        return False, f"异常：{str(e)}"

md_files = glob.glob("**/*.md", recursive=True)
print(f"📄 找到 {len(md_files)} 个 Markdown 文件")

all_passed = True

for md_file in md_files:
    print(f"\n🔍 检查文件：{md_file}")
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.findall(r'```(\w*)\n(.*?)```', content, re.DOTALL)
    print(f"   找到 {len(blocks)} 个代码块")
    
    for i, (lang, code) in enumerate(blocks):
        passed, msg = check_single_block(lang, code)
        if not passed:
            print(f"   ⚠️ 第 {i+1} 个代码块有问题:\n      {msg}\n")
            all_passed = False
        else:
            print(f"   ✅ 第 {i+1} 个代码块通过")

if all_passed:
    print("\n🎉 所有代码块检查通过！")
else:
    print("\n❌ 存在代码问题，请修复后重新提交。")
    sys.exit(1)
