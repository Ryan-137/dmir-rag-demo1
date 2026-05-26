from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import chardet

def load_txt(file_path): #以二进制模式读取，自动诊断编码格式
    with open(file_path,'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        if confidence < 0.7: #设置兜底编码
            encoding ='utf-8'
        loader = TextLoader(file_path, encoding=encoding)
    f.close()
    return loader.load()

file_path="...txt"

documents = load_txt(file_path)   #Document对象
page_content=documents[0].page_content

# 定义分割符列表，按优先级依次使用
separators = ["\n\n", "\n", ".", "，"] # . 是句号，， 是逗号， 是空格
# 创建递归分块器，并传入分割符列表
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=200,
    separators=separators
)
chunks = text_splitter.split_documents(documents)

print(f"{len(chunks)}块")
print("\n=== 文档分块结果 ===")
for i, chunk in enumerate(chunks, 1):
    print(f"\n--- 第 {i} 个文档块 ---")
    print(f"内容: {chunk.page_content}")
    print(f"元数据: {chunk.metadata}")
    print("-" * 50)