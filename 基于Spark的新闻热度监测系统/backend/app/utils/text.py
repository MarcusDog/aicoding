from __future__ import annotations

import hashlib
import html
import re
from collections import Counter

try:
    import jieba
except ImportError:  # pragma: no cover
    jieba = None


ZH_STOPWORDS = {
    "的",
    "了",
    "和",
    "是",
    "在",
    "对",
    "将",
    "与",
    "及",
    "并",
    "或",
    "被",
    "由",
    "等",
    "还",
    "也",
    "已",
    "其",
    "有关",
    "相关",
    "当前",
    "近日",
    "今日",
    "昨天",
    "其中",
    "以及",
    "通过",
    "继续",
    "表示",
    "指出",
    "认为",
    "称",
    "消息",
    "记者",
    "报道",
    "报导",
    "新闻",
    "快讯",
    "图文",
    "视频",
    "全文",
    "阅读",
    "来源",
    "编辑",
    "点击",
    "查看",
    "详情",
    "发布",
    "发布会",
    "官方",
    "回应",
    "进行",
    "已经",
    "仍然",
    "可以",
    "可能",
    "更多",
    "部分",
    "一些",
    "这个",
    "那个",
    "我们",
    "你们",
    "他们",
    "她们",
    "它们",
    "一次",
    "今年",
    "目前",
    "未来",
    "看到",
    "图",
    "文",
    "数据库",
    "公司",
    "据悉",
    "正式",
    "邮箱",
    "责编",
    "日报",
    "人民",
    "人民网",
    "新华网",
    "网易",
    "腾讯",
    "新闻",
    "cn",
    "com",
    "www",
}

EN_STOPWORDS = {
    "the",
    "and",
    "of",
    "in",
    "to",
    "an",
    "a",
    "on",
    "at",
    "by",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "over",
    "under",
    "about",
    "what",
    "both",
    "does",
    "will",
    "have",
    "has",
    "been",
    "more",
    "than",
    "they",
    "them",
    "their",
    "were",
    "was",
    "are",
    "is",
    "it",
    "we",
    "ve",
    "do",
    "who",
    "how",
    "why",
    "when",
    "where",
    "not",
    "out",
    "all",
    "its",
    "his",
    "her",
    "she",
    "you",
    "our",
    "but",
    "can",
    "may",
    "off",
    "one",
    "two",
    "new",
    "said",
    "says",
    "say",
    "after",
    "before",
    "during",
    "through",
    "across",
    "would",
    "could",
    "should",
    "also",
    "just",
    "very",
    "there",
    "here",
    "then",
    "while",
    "onto",
    "upon",
    "including",
    "within",
    "without",
    "because",
    "around",
    "most",
    "some",
    "many",
    "much",
    "such",
    "only",
    "other",
    "still",
    "being",
    "like",
    "world",
    "breaking",
    "update",
    "updates",
    "full",
    "fullquote",
    "quote",
    "quot",
    "amp",
    "lt",
    "gt",
    "http",
    "https",
    "www",
    "com",
    "cn",
    "org",
    "net",
    "reuters",
    "ap",
    "as",
    "us",
    "news",
    "people",
    "qq",
    "kr",
    "tech",
    "daily",
    "email",
    "editor",
    "reporter",
    "gtbhwb",
}

ALLOWED_SHORT_TOKENS = {"ai", "vr", "ar", "it", "us", "uk", "eu", "5g", "6g", "a股", "港股"}
NOISE_PATTERNS = (
    re.compile(r"^[a-z]{1}$"),
    re.compile(r"^[0-9]+$"),
    re.compile(r"^(amp|quot|lt|gt|www|com|cn|org|net)$"),
    re.compile(r"^[a-z]+[0-9]+$"),
    re.compile(r"^[0-9]+[a-z]+$"),
)


def normalize_spaces(text: str) -> str:
    value = html.unescape(text or "")
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def hash_text(value: str) -> str:
    return hashlib.sha256((value or "").encode("utf-8")).hexdigest()


def clean_token(token: str) -> str:
    return normalize_spaces(token).strip(" _-")


def is_noise_token(token: str) -> bool:
    if not token:
        return True
    lowered = token.lower()
    if lowered in ZH_STOPWORDS or lowered in EN_STOPWORDS:
        return True
    if token not in ALLOWED_SHORT_TOKENS and len(token) <= 1:
        return True
    if any(pattern.match(lowered) for pattern in NOISE_PATTERNS):
        return True
    if token.startswith("http"):
        return True
    if token.count(".") >= 1 and len(token) <= 8:
        return True
    if lowered in {"mr", "mrs", "ms", "dr"}:
        return True
    return False


def tokenize(text: str) -> list[str]:
    value = normalize_spaces(re.sub(r"[#%&=/|]+", " ", text or ""))
    if not value:
        return []

    zh_text = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", " ", value)
    tokens: list[str] = []
    if jieba is not None:
        tokens.extend(clean_token(token) for token in jieba.cut(zh_text) if clean_token(token))
    else:
        tokens.extend(clean_token(token) for token in zh_text.split(" ") if clean_token(token))

    english_tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-\+\.]{1,}", value)
    tokens.extend(clean_token(token.lower()) for token in english_tokens if clean_token(token))

    return [token for token in tokens if not is_noise_token(token)]


def extract_keywords(text: str, top_k: int = 8) -> list[str]:
    tokens = tokenize(text)
    if not tokens:
        return []
    weighted_tokens: list[str] = []
    for token in tokens:
        if re.search(r"[\u4e00-\u9fff]", token):
            weighted_tokens.extend([token, token])
        else:
            weighted_tokens.append(token)
    return [item for item, count in Counter(weighted_tokens).most_common(top_k) if count >= 1]


def title_similarity(left: str, right: str) -> float:
    set_left = set(tokenize(left))
    set_right = set(tokenize(right))
    if not set_left or not set_right:
        return 0.0
    return len(set_left & set_right) / len(set_left | set_right)


def build_simhash(text: str) -> str:
    tokens = tokenize(text)
    if not tokens:
        return "0" * 16

    weights = Counter(tokens)
    vector = [0] * 64
    for token, weight in weights.items():
        token_hash = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        for bit in range(64):
            if token_hash & (1 << bit):
                vector[bit] += weight
            else:
                vector[bit] -= weight

    value = 0
    for bit, score in enumerate(vector):
        if score > 0:
            value |= 1 << bit
    return f"{value:016x}"


def simhash_distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()
