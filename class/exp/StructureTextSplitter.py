from langchain_unstructured import UnstructuredLoader
loader=UnstructuredLoader(
    "...pdf",
    chunking_strategy="basic",
    max_characters=1000,
    include_orig_elements=False
)

# loader=UnstructuredLoader(
#     "...pdf",
#     chunking_strategy="by_title",
#     max_characters=1000,
#     include_orig_elements=False
# )

docs=loader.load()
print("分块后langchain的document数量：",len(docs))
i=1
for doc in docs:
    print(f"第{i}个分块的文本：\n{doc.page_content}\n\n")
    i+=1


from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title# 先分区（识别文档元素）

elements = partition_pdf(filename="...pdf")# 按标题分块
chunks = chunk_by_title(elements,
        max_characters=1000,  # 单块最大长度
        # new_after_n_chars=1500,  # 强制换块阈值
        combine_text_under_n_chars=400,  # 合并短文本
        multipage_sections=True          # 跨页章节合并
        )
# 打印分块结果
print("分块后langchain的chunks数量：",len(chunks))
for i, chunk in enumerate(chunks, 1):
    print(f"--- 第 {i} 个分块（标题驱动）---长度：{len(chunk.text)}")
    print(f"内容: {chunk.text[:100]}...\n")
